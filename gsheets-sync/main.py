from http.server import HTTPServer, BaseHTTPRequestHandler
import csv
import json
import os
import re
import subprocess
import sys
import uuid

if len(sys.argv) < 2:
    print("json_path arg not set")
    sys.exit(1)

json_path = sys.argv[1]

random_token = str(uuid.uuid4())
PORT = os.getenv("PORT", 8000)
ENDPOINT = os.getenv("ENDPOINT", "/update")
TOKEN = os.getenv("TOKEN", random_token)

print("TOKEN set to %s" % TOKEN)

def strip_ansi_codes(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def strip_verbose_output(text):
    return re.sub(r'Changing the.*\n?', '', text, flags=re.MULTILINE)

class RequestHandler(BaseHTTPRequestHandler):
    def handle_update(self, post_data):
        out = []

        csv_reader = csv.DictReader(post_data.splitlines())
        for row in csv_reader:
            # omit empty -------------------------------v
            out.append({k: v for k, v in row.items() if v})

        out.sort(key=lambda k : k['code'])

        with open(json_path, "w") as file:
            file.write(json.dumps(out, indent=2))

        print("Wrote %d cards to %s" % (len(out), json_path))

    def reimport_cards_json(self):
        result = subprocess.run([
            "docker",
            "exec",
            "nrdb-dev",
            "bash",
            "-c",
            "php bin/console doctrine:schema:update --force; php bin/console app:import:std -f cards"
        ], capture_output=True, text=True)
        print("stdout: %s" % result.stdout)
        print("stderr: %s" % result.stderr)
        resultMsg = "Card Import return code: %s\n" % result.returncode
        resultMsg += "Card Import stdout: %s\n" % strip_verbose_output(strip_ansi_codes(result.stdout))
        resultMsg += "Card Import stderr: %s" % strip_verbose_output(strip_ansi_codes(result.stderr))
        return resultMsg

    def do_POST(self):
        if self.headers['Authorization'] != TOKEN:
            self.send_response(401)
            self.end_headers()
            return

        if self.path != ENDPOINT:
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            self.handle_update(post_data.decode('utf-8'))
        except Exception as e:
            print("Error in handle_update: %s" % e)
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"update failed")
            return

        result = self.reimport_cards_json()

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(result.encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on port %s..." % PORT)
    httpd.serve_forever()
