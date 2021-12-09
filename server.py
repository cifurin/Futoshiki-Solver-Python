from datetime import date
import futoshiki_solver as fs
import http.server
import socketserver
import csv
from datetime import datetime
import time
from threading import Thread, Event

from http.server import BaseHTTPRequestHandler, HTTPServer

#puzzle = [0] * 25
#row_constraints = [[0 for column in range(4)] for row in range(5)]
#col_constraints = [[0 for column in range(4)] for row in range(5)]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        message = "Hello, World!"
        self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        data = post_data.decode('utf-8')
        data = data.replace('\n', '')
        data = data.replace(',', '')
        print(data)
        fs.squareList = []
        fs.puzzle = [0] * 25
        fs.row_constraints = [[0 for column in range(4)] for row in range(5)]
        fs.col_constraints = [[0 for column in range(4)] for row in range(5)]#
        for i,x in enumerate(data[0:25]):
            fs.puzzle[i] = int(x)
        for i,x in enumerate(data[25:45]):
            #print(i, x, i // 4, i % 4)
            fs.row_constraints[i // 4][i % 4] = int(x)
        for i,x in enumerate(data[45:65]):
            fs.col_constraints[i // 4][i % 4] = int(x)
        print(fs.puzzle)
        print(fs.row_constraints)
        print(fs.col_constraints)
        for x in range(1,26):
            fs.squareList.append(fs.Square(x))

        fs.stop_event = Event()
        fs.puzzle_solved = False

        print("solve puzzle")
        print(datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p"))

        action_thread = Thread(target=fs.solve)
        action_thread.start()

        print("wait up to 5 seconds for puzzle to be solved")
        action_thread.join(timeout=5)

        if not fs.puzzle_solved:
            print("now going to terminate thread as taking too long to solve ..")
            fs.stop_event.set() 
        else:
            print("puzzle has been solved .. here is the solution")
            message =''
            for square in fs.squareList:
                message += str(square.solution[0])
            #print(fs.squareList)

        #fs.solve()
        #fs.print_solution()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        #message = "Hello, World! Here is a POST response"
        self.wfile.write(bytes(message, "utf8"))

with HTTPServer(('', 8000), handler) as server:
    server.serve_forever()