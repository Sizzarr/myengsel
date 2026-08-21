def fix():
    with open('webapp/server.py', 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('@app.post("/api/tools/register")\n    try:', '@app.post("/api/tools/register")\ndef register_number(req: Request, body: RegistrationAction):\n    try:')
    c = c.replace('@app.post("/api/tools/validate-msisdn")\n    try:', '@app.post("/api/tools/validate-msisdn")\ndef validate_msisdn_route(req: Request, body: ValidateMsisdnAction):\n    try:')
    
    with open('webapp/server.py', 'w', encoding='utf-8') as f:
        f.write(c)

fix()
