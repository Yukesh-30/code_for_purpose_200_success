from __future__ import annotations

from app.agents.state import AgentState


def _fmt(n) -> str:
    try:
        v = float(n)
        if abs(v) >= 1_00_00_000:
            return f"₹{v/1_00_00_000:.2f} Cr"
        if abs(v) >= 1_00_000:
            return f"₹{v/1_00_000:.2f} L"
        return f"₹{v:,.0f}"
    except (TypeError, ValueError):
        return str(n)


def _trend_word(val: float) -> str:
    if val > 10:   return "significantly up"
    if val > 2:    return "slightly up"
    if val < -10:  return "significantly down"
    if val < -2:   return "slightly down"
    return "roughly flat"


class ExplanationAgent:
    def explain(self, state: AgentState) -> AgentState:
        status     = state.get("status", "success")
        intent     = state.get("intent", {}).get("intent")
        analysis   = state.get("analysis", {})
        question   = state.get("question", "").lower()
        rows       = state.get("rows", [])
        date_range = state.get("date_range")
        period     = date_range.label if date_range else "the selected period"

        # ── Blocked ───────────────────────────────────────────────────────────
        if status == "blocked":
            state["answer"]      = "Sorry, I can't run that — it looks like a write operation and I only do read-only analytics."
            state["explanation"] = state.get("validation_error") or "Only SELECT queries are allowed."
            return state

        # ── Out of scope ──────────────────────────────────────────────────────
        if status == "out_of_scope":
            original_q = state.get("intent", {}).get("ambiguity", "")
            state["answer"] = (
                f"Hmm, \"{original_q}\" isn't something I can help with — I'm a financial assistant, so I stick to your business data.\n\n"
                "Here's what I'm good at:\n"
                "• **Cashflow** — \"What was my cashflow last month?\"\n"
                "• **Forecasting** — \"Forecast my next 30 days\"\n"
                "• **Expenses** — \"Show expenses by category as a pie chart\"\n"
                "• **Anomalies** — \"Find unusual transactions\"\n"
                "• **Invoices** — \"Which invoices are overdue?\"\n"
                "• **Risk** — \"What's my current risk score?\"\n\n"
                "What would you like to know about your business?"
            )
            state["explanation"] = "Question is outside financial analytics scope."
            return state

        # ── Conversational — general financial question, no DB needed ─────────
        if status == "conversational":
            question_text = state.get("question", "")
            answer = self._answer_conversationally(question_text)
            state["answer"]      = answer
            state["explanation"] = "Answered from financial knowledge — no database query needed."
            return state
        if status == "needs_clarification":
            ambiguity = state.get("intent", {}).get("ambiguity", "")
            state["answer"]      = ambiguity or "Could you be a bit more specific? What are you looking for — cashflow, expenses, invoices, forecast, or something else?"
            state["explanation"] = "Need more context to query your financial data."
            return state

        # ── Insufficient data ─────────────────────────────────────────────────
        if status == "insufficient_data":
            reason = analysis.get("reason", "Not enough data for this request.")
            state["answer"]      = f"I don't have enough data for that right now. {reason}"
            state["explanation"] = reason
            return state

        # ── Complex multi-step ────────────────────────────────────────────────
        if intent == "complex":
            return self._explain_complex(state, rows, period)

        # ── Forecast ─────────────────────────────────────────────────────────
        if intent == "forecast":
            return self._explain_forecast(state, rows)

        # ── Anomaly ───────────────────────────────────────────────────────────
        if intent == "anomaly":
            return self._explain_anomaly(state, rows, analysis, period)

        # ── Analytics ────────────────────────────────────────────────────────
        return self._explain_analytics(state, rows, analysis, question, period)

    # ── Forecast explanation ──────────────────────────────────────────────────
    def _answer_conversationally(self, question: str) -> str:
        """
        Answer general financial questions using LLM if available,
        or a knowledge-based fallback.
        """
        # Try LLM first
        try:
            from app.llm.client import get_llm
            llm = get_llm()
            if llm.enabled:
                system = (
                    "You are FlowSight AI, a friendly financial assistant for small businesses. "
                    "Answer the user's question conversationally and helpfully. "
                    "Keep answers concise (2-4 sentences). "
                    "If the question is about a financial concept, explain it simply. "
                    "If it's a greeting or small talk, respond warmly and briefly. "
                    "Do NOT make up specific numbers or data — only explain concepts."
                )
                answer = llm.chat(system, question, max_tokens=200, temperature=0.7)
                if answer:
                    return answer
        except Exception:
            pass

        # Fallback: knowledge-based responses for common financial questions
        q = question.lower()

        if any(w in q for w in ("burn rate", "burn")):
            return "Burn rate is how fast you're spending money — typically measured monthly. If you spend ₹5L/month and have ₹50L in the bank, your runway is 10 months. Want me to calculate yours from your actual transactions?"

        if any(w in q for w in ("runway", "how long")):
            return "Runway is how many months you can operate before running out of cash, based on your current burn rate. Ask me 'what is my runway?' and I'll calculate it from your real data."

        if any(w in q for w in ("cashflow", "cash flow")):
            return "Cashflow is the net movement of money in and out of your business — credits minus debits. Positive cashflow means more coming in than going out. Want to see yours?"

        if any(w in q for w in ("working capital",)):
            return "Working capital = current assets minus current liabilities. It measures your ability to cover short-term obligations. A positive number means you're in good shape operationally."

        if any(w in q for w in ("invoice", "receivable")):
            return "Invoices are bills you've sent to customers. Receivables are the money owed to you. Delayed payments hurt cashflow — want me to show your overdue invoices?"

        if any(w in q for w in ("hello", "hi", "hey", "good morning", "good evening")):
            return "Hey! I'm FlowSight AI. Ask me anything about your business finances — cashflow, invoices, forecasts, expenses, or risk scores."

        if any(w in q for w in ("thank", "thanks")):
            return "Happy to help! Let me know if you have more questions about your finances."

        if any(w in q for w in ("what can you do", "help", "what do you do")):
            return (
                "I can help you understand your business finances:\n"
                "• **Cashflow** — trends, comparisons, forecasts\n"
                "• **Invoices** — overdue, pending, customer analysis\n"
                "• **Expenses** — breakdown by category or vendor\n"
                "• **Anomalies** — unusual transactions\n"
                "• **Risk** — liquidity and default risk scores\n\n"
                "Just ask naturally — like you'd ask a colleague."
            )

        # Generic fallback
        return (
            f"That's a good question! I'm best at answering questions about your actual business data — "
            f"cashflow, invoices, expenses, forecasts, and risk. "
            f"Try asking something like 'what was my cashflow last month?' or 'show me overdue invoices'."
        )

    def _explain_forecast(self, state: AgentState, rows: list) -> AgentState:
        fc       = state.get("forecast", {})
        end_bal  = fc.get("projected_ending_balance", 0)
        neg_days = fc.get("negative_cashflow_days", 0)
        horizon  = fc.get("horizon_days", 30)
        method   = fc.get("method", "statistical model")
        avg_in   = fc.get("avg_inflow",  0)
        avg_out  = fc.get("avg_outflow", 0)
        avg_net  = fc.get("avg_net",     avg_in - avg_out)
        history  = fc.get("history_days", 0)

        tone = "looks healthy" if end_bal > 0 and neg_days == 0 else "needs attention"

        state["answer"] = (
            f"Based on your last {history} days of transactions, here's what the next {horizon} days look like:\n\n"
            f"Your projected closing balance will be **{_fmt(end_bal)}** — that {tone}.\n"
            f"On average, you're bringing in {_fmt(avg_in)}/day and spending {_fmt(avg_out)}/day, "
            f"giving you a net of {_fmt(avg_net)}/day."
            + (f"\n\n⚠️ Heads up — I'm seeing **{neg_days} days** where your cashflow goes negative. "
               "You'll want to accelerate invoice collections or hold off on non-critical payments during those periods."
               if neg_days > 0 else
               "\n\n✅ Good news — no negative cashflow days projected in this window.")
        )
        state["explanation"] = (
            f"Forecast method: {method}. "
            f"Built from {history} days of historical transaction data. "
            "The chart shows predicted inflow, outflow, and closing balance day by day."
        )
        return state

    # ── Anomaly explanation ───────────────────────────────────────────────────
    def _explain_anomaly(self, state: AgentState, rows: list,
                         analysis: dict, period: str) -> AgentState:
        count  = analysis.get("anomaly_count", len(rows))
        method = analysis.get("method", "statistical analysis")
        avg    = analysis.get("average_amount", 0)

        if count == 0:
            state["answer"] = (
                f"Good news — I didn't find any unusual transactions in {period}. "
                "Everything looks within normal range."
            )
        else:
            top = rows[0] if rows else {}
            state["answer"] = (
                f"I found **{count} unusual transaction{'s' if count != 1 else ''}** in {period}.\n\n"
                f"The most notable one: {_fmt(top.get('amount'))} "
                f"({top.get('transaction_type', '')}) "
                f"at {top.get('merchant_name') or top.get('category', 'unknown')} "
                f"on {top.get('transaction_date', '')}.\n\n"
                f"These stand out because they're significantly different from your average transaction of {_fmt(avg)}. "
                "Worth reviewing to make sure they're legitimate."
            )
        state["explanation"] = (
            f"Detection method: {method}. "
            f"Analysed {analysis.get('lookback_transactions', len(rows))} transactions. "
            "Flagged transactions deviate significantly from your normal spending patterns."
        )
        return state

    # ── Analytics explanation ─────────────────────────────────────────────────
    def _explain_analytics(self, state: AgentState, rows: list,
                            analysis: dict, question: str, period: str) -> AgentState:
        totals = analysis.get("totals")

        # Cashflow summary
        if totals:
            net = totals.get("net_cashflow", 0)
            inf = totals.get("inflow", 0)
            out = totals.get("outflow", 0)
            direction = "positive" if float(net) >= 0 else "negative"
            health    = "You're in good shape." if float(net) >= 0 else "You're spending more than you're earning — worth reviewing."
            state["answer"] = (
                f"Your cashflow for {period}: **{_fmt(net)}** ({direction}).\n\n"
                f"You brought in {_fmt(inf)} and spent {_fmt(out)}. {health}"
            )
            state["explanation"] = (
                f"Calculated as total credits minus total debits from bank_transactions for {period}. "
                "Grouped daily so you can see the trend in the chart."
            )
            return state

        # Category breakdown (pie/bar)
        by_cat = analysis.get("by_category")
        if by_cat:
            top_cat = max(by_cat, key=by_cat.get)
            total   = sum(by_cat.values())
            pct     = round(by_cat[top_cat] / total * 100, 1) if total else 0
            state["answer"] = (
                f"Here's your expense breakdown for {period}:\n\n"
                f"Your biggest spending category is **{top_cat}** at {_fmt(by_cat[top_cat])} "
                f"({pct}% of total spend). "
                f"Total expenses: {_fmt(total)} across {len(by_cat)} categories."
            )
            state["explanation"] = "Expenses grouped by category. The chart shows the proportion of each category."
            return state

        # Invoices
        if rows and "invoice_number" in rows[0]:
            overdue   = sum(1 for r in rows if r.get("status") == "overdue")
            pending   = sum(1 for r in rows if r.get("status") == "pending")
            paid      = sum(1 for r in rows if r.get("status") == "paid")
            total_val = sum(float(r.get("invoice_amount") or 0) for r in rows)
            state["answer"] = (
                f"You have **{len(rows)} invoices** totalling {_fmt(total_val)}:\n"
                f"• {paid} paid ✅\n"
                f"• {pending} pending ⏳\n"
                f"• {overdue} overdue ⚠️"
                + (f"\n\nThe {overdue} overdue invoice{'s' if overdue != 1 else ''} need immediate attention — "
                   "they're directly impacting your cashflow." if overdue > 0 else "")
            )
            state["explanation"] = "Invoice data from invoice_records table."
            return state

        # Vendor payments
        if rows and "vendor_name" in rows[0]:
            total = sum(float(r.get("payment_amount") or 0) for r in rows)
            top   = rows[0]
            state["answer"] = (
                f"You have **{len(rows)} vendor payment{'s' if len(rows)!=1 else ''}** due, "
                f"totalling {_fmt(total)}.\n\n"
                f"Largest upcoming payment: {_fmt(top.get('payment_amount'))} to "
                f"**{top.get('vendor_name')}** due {top.get('due_date')}."
            )
            state["explanation"] = "Vendor payment obligations from vendor_payments table."
            return state

        # Loans
        if rows and "loan_type" in rows[0]:
            total_emi = sum(float(r.get("emi_amount") or 0) for r in rows)
            total_out = sum(float(r.get("outstanding_amount") or 0) for r in rows)
            state["answer"] = (
                f"You have **{len(rows)} active loan{'s' if len(rows)!=1 else ''}**:\n"
                f"• Total monthly EMI: {_fmt(total_emi)}\n"
                f"• Total outstanding: {_fmt(total_out)}"
            )
            state["explanation"] = "Loan data from loan_obligations table."
            return state

        # Risk scores
        if rows and "liquidity_score" in rows[0]:
            r = rows[0]
            band  = str(r.get("overall_risk_band", "unknown")).upper()
            liq   = r.get("liquidity_score", "—")
            emoji = {"SAFE": "✅", "MODERATE": "⚠️", "HIGH": "🔴", "CRITICAL": "🚨"}.get(band, "")
            state["answer"] = (
                f"Your current risk profile: **{band}** {emoji}\n\n"
                f"• Liquidity score: {liq}/100\n"
                f"• Default risk: {r.get('default_risk_score', '—')}\n"
                f"• Overdraft risk: {r.get('overdraft_risk_score', '—')}\n"
                f"• Working capital: {r.get('working_capital_score', '—')}"
            )
            state["explanation"] = f"Latest risk scores as of {r.get('forecast_date', 'today')}."
            return state

        # Balance
        if rows and "closing_balance" in rows[0]:
            r = rows[0]
            state["answer"] = (
                f"Your current closing balance is **{_fmt(r.get('closing_balance'))}** "
                f"as of {r.get('transaction_date', 'latest')}."
            )
            state["explanation"] = "Latest balance_after_transaction from your most recent bank transaction."
            return state

        # Expenses
        if rows and "expense_name" in rows[0]:
            total = sum(float(r.get("amount") or 0) for r in rows)
            state["answer"] = (
                f"Total expenses for {period}: **{_fmt(total)}** "
                f"across {len(rows)} record{'s' if len(rows)!=1 else ''}."
            )
            state["explanation"] = f"Expense records for {period} sorted by amount."
            return state

        # Customers / buyers
        if rows and "customer_name" in rows[0]:
            top = rows[0]
            total_inv = sum(float(r.get("total_invoiced") or 0) for r in rows)
            state["answer"] = (
                f"Your biggest customer is **{top.get('customer_name')}** "
                f"with {_fmt(top.get('total_invoiced'))} invoiced "
                f"({top.get('invoice_count', 0)} invoices).\n\n"
                f"Top {min(len(rows), 5)} customers account for {_fmt(total_inv)} in total."
            )
            state["explanation"] = "Customers ranked by total invoiced amount from your invoice records."
            return state
            top = rows[0]
            txn_type = top.get("transaction_type", "")
            state["answer"] = (
                f"Your largest {txn_type} transaction in {period} was **{_fmt(top.get('amount'))}** "
                f"— {top.get('category', '')} at {top.get('merchant_name') or 'unknown'} "
                f"on {top.get('transaction_date', '')}."
            )
            state["explanation"] = f"Transactions in {period} sorted by amount descending."
            return state

        # Generic fallback
        state["answer"]      = f"I found **{len(rows)} record{'s' if len(rows)!=1 else ''}** matching your query."
        state["explanation"] = "Results are grounded in your real database — no estimates."
        return state

    # ── Complex multi-step explanation ────────────────────────────────────────
    def _explain_complex(self, state: AgentState, rows: list, period: str) -> AgentState:
        driver   = state.get("driver_analysis", {})
        recs     = state.get("recommendations", [])
        summary  = state.get("driver_summary", "")
        fc       = state.get("step_results", {}).get("forecast", {})
        plan     = state.get("plan", {})
        n_months = plan.get("n_months", 2)
        periods  = plan.get("periods", {})
        curr     = periods.get("current", {})
        prev     = periods.get("previous", {})

        step_results = state.get("step_results", {})
        curr_data    = step_results.get("current_cashflow",  {})
        prev_data    = step_results.get("previous_cashflow", {})

        # Summary
        state["summary"] = (
            f"Period: {curr.get('start')} to {curr.get('end')} vs "
            f"{prev.get('start')} to {prev.get('end')}. "
            f"Current net: {_fmt(curr_data.get('net', 0))}. "
            f"Previous net: {_fmt(prev_data.get('net', 0))}."
        ) if curr_data else summary

        # Root cause
        root_parts = []
        if driver.get("inflow_change", 0) < 0:
            root_parts.append(
                f"Revenue dropped by {_fmt(abs(driver['inflow_change']))} "
                f"({abs(driver.get('net_pct_change', 0)):.1f}% decline in inflow)."
            )
        if driver.get("outflow_change", 0) > 0:
            root_parts.append(f"Expenses increased by {_fmt(driver['outflow_change'])}.")
        top_cats = driver.get("top_categories", [])
        if top_cats:
            root_parts.append(
                f"Biggest expense driver: {top_cats[0].get('category')} "
                f"at {_fmt(top_cats[0].get('spent', 0))} ({top_cats[0].get('pct', 0):.1f}% of spend)."
            )
        state["root_cause"] = " ".join(root_parts) if root_parts else "Insufficient data for root cause."

        # Build conversational answer
        parts = []

        # Part 1: Comparison
        if summary:
            parts.append(summary)

        # Part 2: Forecast
        if fc and fc.get("projected_ending_balance") is not None:
            end_bal  = fc.get("projected_ending_balance", 0)
            neg_days = fc.get("negative_cashflow_days", 0)
            horizon  = fc.get("horizon_days", 30)
            parts.append(
                f"Looking ahead {horizon} days, your projected closing balance is **{_fmt(end_bal)}**."
                + (f" ⚠️ {neg_days} days with negative cashflow expected — act now." if neg_days > 0 else "")
            )

        # Part 3: Recommendations
        if recs:
            rec_lines = [f"{i+1}. **{r['action']}** — {r['reason'][:90]}" for i, r in enumerate(recs[:3])]
            parts.append("Here's what I'd recommend:\n" + "\n".join(rec_lines))

        state["answer"] = "\n\n".join(parts) if parts else "Analysis complete."
        state["explanation"] = (
            "Multi-step analysis: calendar-accurate period comparison, "
            "vendor/category driver breakdown, ML-powered forecast, "
            "and actionable recommendations — all from your real transaction data."
        )
        return state
