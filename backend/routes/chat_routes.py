from flask import Blueprint, request, jsonify
from models import db, ChatSession, ChatMessage, BusinessUser
from services.auth_service import token_required
from routes.chatbot_routes import (
    resolve_query_context, 
    select_relevant_tables, 
    generate_sql_query, 
    execute_raw_sql, 
    generate_business_insight
)
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/start', methods=['POST'])
@token_required
def start_session(current_user):
    data = request.get_json()
    if not data or 'business_id' not in data:
        return jsonify({"error": "Missing business_id in request"}), 400

    user_id = current_user.get('user_id')
    business_id = data['business_id']

    # Verify that the user belongs to this business
    mapping = BusinessUser.query.filter_by(user_id=user_id, business_id=business_id).first()
    if not mapping:
        return jsonify({"error": "User does not have access to this business"}), 403

    try:
        new_session = ChatSession(
            user_id=user_id,
            business_id=business_id,
            session_name=data.get('session_name', 'New Chat Session')
        )
        db.session.add(new_session)
        db.session.commit()

        return jsonify({"session_id": new_session.id}), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/sessions', methods=['POST'])
@token_required
def list_sessions(current_user):
    data = request.get_json()
    if not data or 'business_id' not in data:
        return jsonify({"error": "Missing business_id in request"}), 400

    user_id = current_user.get('user_id')
    business_id = data['business_id']

    # Verify that the user belongs to this business
    mapping = BusinessUser.query.filter_by(user_id=user_id, business_id=business_id).first()
    if not mapping:
        return jsonify({"error": "User does not have access to this business"}), 403

    try:
        sessions = ChatSession.query.filter_by(business_id=business_id, user_id=user_id).order_by(ChatSession.id.desc()).all()
        return jsonify({
            "sessions": [
                {"id": s.id, "session_name": s.session_name} for s in sessions
            ]
        })
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/history', methods=['POST'])
@token_required
def fetch_history(current_user):
    data = request.get_json()
    if not data or 'session_id' not in data:
        return jsonify({"error": "Missing session_id in request"}), 400

    session_id = data['session_id']
    limit = data.get('limit', 50)

    # Verify session belongs to user
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.get('user_id')).first()
    if not session:
        return jsonify({"error": "Chat session not found or access denied"}), 404

    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.id.asc()).limit(limit).all()

    return jsonify({
        "messages": [
            {"role": msg.sender_type, "text": msg.message_text} for msg in messages
        ]
    })

@chat_bp.route('/message', methods=['POST'])
@token_required
def store_message(current_user):
    data = request.get_json()
    required = ['session_id', 'business_id', 'role', 'message']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    user_id = current_user.get('user_id')
    
    # Verify session belongs to user
    session = ChatSession.query.filter_by(id=data['session_id'], user_id=user_id).first()
    if not session:
        return jsonify({"error": "Chat session not found or access denied"}), 404

    try:
        new_msg = ChatMessage(
            session_id=data['session_id'],
            business_id=data['business_id'],
            sender_type=data['role'], # 'user' or 'ai'
            message_text=data['message']
        )
        db.session.add(new_msg)
        db.session.commit()

        return jsonify({"message": "Saved successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/query', methods=['POST'])
@token_required
def chat_query(current_user):
    data = request.get_json()
    if not data or 'session_id' not in data or 'query' not in data:
        return jsonify({"error": "Missing session_id or query in request body"}), 400

    session_id = data['session_id']
    user_query = data['query']
    user_id = current_user.get('user_id')

    # 1. Verify session and get business_id
    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"error": "Chat session not found or access denied"}), 404
    
    business_id = session.business_id

    try:
        # 2. Save User Message
        new_user_msg = ChatMessage(
            session_id=session_id,
            business_id=business_id,
            sender_type='user',
            message_text=user_query
        )
        db.session.add(new_user_msg)
        db.session.commit()

        # 3. Get History for Context (last 5)
        history_msgs = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.id.desc()).limit(6).all()
        # Exclude the current message we just added for context resolve (but usually it's fine to include)
        history_data = [{"role": m.sender_type, "text": m.message_text} for m in reversed(history_msgs)]

        # 4. Resolve Context
        context = resolve_query_context(user_query, history_data[:-1]) # use previous history
        refined_query = context['refined_query']
        entities = context['entities']
        
        # Combine refined query and entities for broader LLM context
        combined_query = f"Refined Query: {refined_query} | Contextual Entities: {json.dumps(entities)}"

        # 5. Select Tables
        tables_res = select_relevant_tables(combined_query)
        tables = tables_res.get('tables', [])

        # 6. Generate SQL
        sql_res = generate_sql_query(combined_query, tables, business_id)
        sql = sql_res.get('sql')

        # 7. Execute SQL
        data_rows = execute_raw_sql(sql)

        # 8. Generate Insight
        insight = generate_business_insight(combined_query, sql, data_rows, user_id, business_id)

        # 9. Explanation (Using insight summary as per requirement)
        explanation = insight.get('summary', "Based on the data analysis, here are the results.")

        # 10. Save AI Response
        new_ai_msg = ChatMessage(
            session_id=session_id,
            business_id=business_id,
            sender_type='ai',
            message_text=explanation
        )
        db.session.add(new_ai_msg)
        db.session.commit()

        return jsonify({
            "query": user_query,
            "sql": sql,
            "data": data_rows,
            "insight": {
                "answer": explanation,
                "insight": insight.get('summary'),
                "risk": "Confidence Score: " + str(insight.get('confidence', 'N/A'))
            },
            "explanation": explanation,
            "tables_used": tables
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500