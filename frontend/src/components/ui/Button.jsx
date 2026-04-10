import * as React from "react"
import { cn } from "../../lib/utils"

const Button = React.forwardRef(({ className, variant = "default", size = "default", asChild = false, ...props }, ref) => {
  const Comp = "button"
  
  const variants = {
    default: "bg-gradient-to-r from-primary to-secondary text-primary-text shadow hover:opacity-90",
    destructive: "bg-danger text-white hover:bg-danger/90",
    outline: "border border-border bg-transparent hover:bg-white/5 text-primary-text",
    secondary: "bg-secondary-background text-primary-text hover:bg-white/10",
    ghost: "hover:bg-white/5 hover:text-primary-text text-muted-text",
    link: "text-primary underline-offset-4 hover:underline",
  }

  const sizes = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3 text-xs",
    lg: "h-11 rounded-md px-8",
    icon: "h-10 w-10",
  }

  return (
    <Comp
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"

export { Button }
