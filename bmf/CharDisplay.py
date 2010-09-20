
class CharDisplay:

  def __init__(self,log,rows=20,columns=48):

     self.msgcallback=log
     self.rows = rows
     self.columns = columns
     self.msg = [ "", "" ]
     j=0
     while j < self.rows:
         self.msg.append( " " * self.columns )
         j+=1

  def clear(self):
     j=0
     while j < self.rows:
         self.msg[j]= " " * self.columns 
         j+=1

  def writeStringXY(self,x,y,str):
     """
        display a given str at row y in column x.

     """

     # refuse to draw out of bounds...
     if ( x > self.columns ) or ( y >= self.rows ):
        self.msgcallback( "origin off of screen: row=%d, column=%d" % ( y, x ) )
        return

     #print "write, self.msg[%d] before: +%s+" % ( y, self.msg[y] )

     xend = x + len(str)
     if xend < self.columns:
         # if it fits on the screen, just substitute the string within the line.
         self.msg[y]= self.msg[y][0:x] + str + self.msg[y][xend:]
     else:
         # if it replaces the end of the line, then change the end...
         str_cutoff = len(str) - (xend - self.columns)
         self.msg[y]= self.msg[y][0:x] + str[0:str_cutoff]


