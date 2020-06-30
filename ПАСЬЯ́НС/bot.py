import pyautogui
import win32api
import win32con
import time
import numpy as np
import copy
PATH = r'C:\Users\lachl\Desktop\Python\exapunks_bots\array\\'
FUTURE = 3

class Bot():
    def __init__(self):
        self.complete = False
        self.load_images()
        self.table = [[] for i in range(9)]
        self.special_place = []
        self.table_map = [[] for i in range(9)]
        self.face = ['heart','diamond','spade','club']
        self.numeric = [f'r{i}' for i in range(6,11)]
        self.numeric.extend([f'b{i}' for i in range(6,11)])
        self.setup_map()
        #select the game screen
        win32api.SetCursorPos((1490,631))
        time.sleep(1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,1490,631)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,1490,631)
        self.main()
    
    def setup_map(self):
        array = []
        for i in range(370,1576,134):
            for j in range(464,674,30):
                array.append((i,j))
        print(len(array))
        for i in range(9):
            for j in range(7):
                self.table_map[i].append(array.pop(0))

    
    def load_images(self):
        #the cards are saved in numpy arrays; import them for use
        self.images = []
        self.names = ['r10','r9','r8','r7','r6','b10','b9','b8','b7','b6','heart','diamond','spade','club']
        for i in self.names:
            self.images.append(np.load(f'{PATH}{i}.npy'))
        
    def populate_table(self):
        board = []
        for i in range(9):
            self.table[i].clear()
        #this selects card numbers in fullscreen 1920 1080
        for i in range(370,1576,134):
            for j in range(464,584,30):
                img = np.array(pyautogui.screenshot(region=(i,j,12,12)))
                for c,k in enumerate(self.images):
                    if (img == k).all():
                        board.append(self.names[c])
        #print(len(board))
        for i in range(9):
            for j in range(4):
                self.table[i].append(board.pop(0))
        self.special_place = []

    def generate_loop(self):
        for i in range(9):
            for j in range(9):
                yield i,j

    def find_moves(self, this_board,this_special,hypothetical):
        print(f"the table looks like {this_board}")
        move = None
        if this_special:
            depth, this_card = 1, [this_special[0],(1380,227)] #this is a special position. It isnt in the position map. 
            for j in range(9):
                if len(this_board[j])<2: continue
                if self.available_move(None,[this_special[0],(0,0)],[this_board[j][-1],(j,len(this_board[j])-1)], None): #I cannot tell why the first and last arguments are required. I dont think they are. 
                    this_special.pop(-1)
                    if not hypothetical: self.moves.append(((1380,227),self.table_map[j][len(this_board[j])-1])) #****************
                    return 0
                
        if not move:    
            for i,j in self.generate_loop():
                if i == j or len(this_board[i]) == 0 or len(this_board[j]) == 0: continue
                this_card = [this_board[i][-1],(i,len(this_board[i])-1)]
                depth, this_card = self.get_depth(i,this_card,this_board) if this_card[0] in self.numeric else self.get_face_depth(i,this_card,this_board)
                that_card = [this_board[j][-1],(j,len(this_board[j])-1)]
                move = self.available_move(i,this_card,that_card,depth)
                if move: 
                    break
        #do what we can without taking a free column; then take a free column if we must
        if not move:
            for i, j in self.generate_loop():
                if len(this_board[i]) == 0: continue
                this_card = [this_board[i][-1],(i,len(this_board[i])-1)]
                if not this_card[0] in self.face and not this_card[0] in ['r10','b10']: continue
                if this_card[0] in self.face: depth, this_card = self.get_face_depth(i,this_card,this_board)
                if len(this_board[j]) == 0:
                    move = (self.table_map[this_card[1][0]][this_card[1][1]],self.table_map[j][0])
                    break
                    
        if not move and not this_special:
            for i,j in self.generate_loop():
                if i == j or len(this_board[i]) < 2 or len(this_board[j]) == 0: continue
                this_card = [this_board[i][-2],(i,len(this_board[i])-2)]
                that_card = [this_board[j][-1],(j,len(this_board[j])-1)]
                if self.available_move(i,this_card,that_card,depth):
                    this_special.append(this_board[i].pop(-1))
                    self.moves.append((self.table_map[i][-1],(1380,227)))
                    print("no error")
                    return 0
            for i,j in self.generate_loop():
                if i == j or len(this_board[i]) == 0 or len(this_board[j]) < 2: continue
                this_card = [this_board[i][-1],(i,len(this_board[i])-1)]
                that_card = [this_board[j][-2],(j,len(this_board[j])-2)]
                if self.available_move(i,this_card,that_card,depth):
                    this_special.append(this_board[j].pop(-1))
                    self.moves.append((self.table_map[j][-1],(1380,227))) 
                    print("no error")
                    return 0
        
        print(f'this card {this_card}, that card {that_card}') 
        
        if (not hypothetical) and move: 
            passed = self.test_future()
        if move:
            this_board[j].extend(this_board[i][-depth:])
            this_board[i] = this_board[i][:-depth]
            if not hypothetical and passed:
                self.moves.append(move)
            elif not hypothetical and not passed:
                print("no future")
                return 2
                print("no error")
            return 0
        print("not found")
        return 1
    
    def test_future(self):
        test_table = copy.deepcopy(self.table)
        test_special = copy.deepcopy(self.special_place)
        for i in range(FUTURE):
            print(f"Test {i}")
            if self.find_moves(test_table,test_special,True):
                return False
        return True
        
    def available_move(self,i,this_card,that_card,depth):
        if this_card[0] in self.face and that_card[0] == this_card[0]:
            pass
        elif (this_card[0] in self.numeric and not that_card[0] in self.face) and (that_card[0][0] != this_card[0][0] and int(that_card[0][1:]) == int(this_card[0][1:])+1):
            pass
        else:
            return None
        print(f' this card that card {this_card}, {that_card}')
        return (self.table_map[this_card[1][0]][this_card[1][1]],self.table_map[that_card[1][0]][that_card[1][1]])
        
    def get_depth(self, i, this_card,this_board):
        depth = 1
        while True:
            if len(this_board[i]) == depth: 
                return (depth,this_card)
            if this_board[i][-depth-1] in self.face: 
                return (depth,this_card)
            if this_board[i][-depth-1][0] == this_card[0][0]: 
                return (depth,this_card)
            if int(this_board[i][-depth-1][1:]) != int(this_card[0][1:])+1: 
                return (depth,this_card)
            else:
                depth += 1
                #print(f'{this_board[i][-depth]}, {depth}')
                this_card = [this_board[i][-depth],(i,len(this_board[i])-depth)]
    
    def get_face_depth(self,i,this_card,this_board):
        depth = 1
        while True:
            if len(this_board[i]) == depth:
                return (depth,this_card)
            if this_board[i][-depth-1] in self.numeric:
                return (depth,this_card)
            if this_board[i][-depth-1] != this_card[0]:
                return (depth,this_card)
            else:
                depth +=1
                #print(f'{this_board[i][-depth]}, {depth}')
                this_card = [this_board[i][-depth],(i,len(this_board[i])-depth)]
        
        
    def test_win(self):
        win = []
        win.append(['heart','heart','heart','heart'] in self.table)
        win.append(['diamond','diamond','diamond','diamond'] in self.table)
        win.append(['spade','spade','spade','spade'] in self.table)
        win.append(['club','club','club','club'] in self.table)
        win.append(['r10','r9','r8','r7','r6'] in self.table)
        win.append(['b10','b9','b8','b7','b6'] in self.table)
        return all(win)


    def enact_move(self,pos_map): #move looks like [(x,y),(x2,y2)]
        win32api.SetCursorPos(pos_map[0])
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,pos_map[0][0],pos_map[0][1])
        time.sleep(0.5)
        win32api.SetCursorPos(pos_map[1])
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,pos_map[1][0],pos_map[1][1])
        time.sleep(0.5)
    
    def main(self):
        for games in range(3):
            self.moves = []
            self.populate_table()
            errormap = ["no error","no move found","cant see enough future moves"]
            for i in range(30):
            #while not self.find_moves(self.table,False):
                #pass
                print(f"Move number {i}")
                print(errormap[self.find_moves(self.table,self.special_place, False)])
            #print(self.moves)
            time.sleep(2)
            print(f'there are {len(self.moves)} moves')
            while self.moves:
                self.enact_move(self.moves.pop(0))
            print(f'did we win? {self.test_win()}')
            time.sleep(30)
            win32api.SetCursorPos((1364,891))
            time.sleep(0.2)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,1364,891)
            time.sleep(0.2)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,1364,891)
            time.sleep(10)

bot = Bot()
