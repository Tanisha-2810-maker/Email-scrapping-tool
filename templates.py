def outreach_template(company_name=""):
    subject = "Collaboration Opportunity"

    greeting = f"Hi {company_name} Team," if company_name else "Hi Team,"

    body = f"""{greeting}

I hope you're doing well.

I came across your website and was impressed by your work. I wanted to connect and explore possible collaboration opportunities.

Looking forward to hearing from you.

Best regards,
Tanisha Sen
"""

    return subject, body
