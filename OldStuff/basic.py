import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from time import sleep
class plotObject():
    def __init__(self):
        self.x = []
        self.y = []
        self.fig = plt.figure()
        self.ax = plt.axes(xlim=(0, 2), ylim=(-2, 2))
    
    def init(self):
        self.line, = self.ax.plot([], [], lw=2)
        self.line.set_data([], [])
        return self.line,

    def animate(self,i):
        self.x.append(i)
        self.y.append(np.sin(i))
        

        #self.ax.set_xlim(0,max(self.x)) #set x limit of axis    
        #self.ax.set_ylim(min(self.x),max(self.y))

        self.line.set_data(self.x, self.y)
        sleep(1)

        self.ax.set_xbound(lower=0, upper=max(self.x))
        self.ax.set_ybound(lower=min(self.x), upper=max(self.y))
        

        return self.line,

    def startplot(self):
        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init,
                                    interval=1, blit=True)
        plt.show()



    
		


# x = []
# y = []

# #self.livePlot = FuncAnimation(self.fig, self.live, init_func=self.figureTitles, interval=1, blit=True)
# # First set up the figure, the axis, and the plot element we want to animate
# fig = plt.figure()
# ax = plt.axes(xlim=(0, 2), ylim=(-2, 2))
# line, = ax.plot([], [], lw=2)

# # initialization function: plot the background of each frame
# def init():
#     line.set_data([], [])
#     return line,

# # animation function.  This is called sequentially
# def animate(i):
#     x.append(i)
#     y.append(np.sin(i))
#     line.set_data(x, y)
#     return line,

p = plotObject()
p.startplot()


