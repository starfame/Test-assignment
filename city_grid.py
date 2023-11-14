import random
import math

from matplotlib import patches, pyplot as plt
from collections import deque


class DefaultBlock:
    def __init__(self, color, block_type):
        self.type = block_type
        self.color = color

    def __str__(self):
        return self.color


class CityGrid:
    def __init__(self, n, m, occupancy_percentage=30, round_up=False, range_r=1):
        self.n = n
        self.m = m
        self.grid = [[None for _ in range(m)] for _ in range(n)]
        self.range_r = range_r

        blocks = n * m

        occupancy_blocks = self._calculate_blocks(occupancy_percentage, blocks, round_up)

        self.obstructed_block = DefaultBlock("green", "o")
        self.tower_block = DefaultBlock("red", "t")
        self.range_block = DefaultBlock("red", "r")

        while occupancy_blocks > 0:
            x = random.randint(0, n-1)
            y = random.randint(0, m-1)

            if self.grid[x][y] is None:
                self.grid[x][y] = self.obstructed_block
                occupancy_blocks -= 1

    def __str__(self):
        result = ""

        for y in range(self.m)[::-1]:
            for x in range(self.n):
                result += str(self.grid[x][y])
                result += ' '
            result += '\n'

        return result

    def _place_tower(self, x, y, range_r):
        if self.grid[x][y] == self.obstructed_block:
            return False

        for i in range(max(0, x - range_r), min(self.n, x + range_r + 1)):
            for j in range(max(0, y - range_r), min(self.m, y + range_r + 1)):
                if self.grid[i][j] != self.obstructed_block:
                    self.grid[i][j] = self.range_block

        self.grid[x][y] = self.tower_block

    def greedy_optimization(self):
        while not self._all_covered():
            best_location = None
            best_coverage = 0

            for x in range(self.n):
                for y in range(self.m):
                    if self.grid[x][y] is None:
                        coverage = self._calculate_coverage(x, y)
                        if coverage > best_coverage:
                            best_coverage = coverage
                            best_location = (x, y, self.range_r)

            if best_location:
                self._place_tower(*best_location)

    def _calculate_coverage(self, x, y):
        coverage = 0
        for i in range(max(0, x - self.range_r), min(self.n, x + self.range_r + 1)):
            for j in range(max(0, y - self.range_r), min(self.m, y + self.range_r + 1)):
                if self.grid[i][j] is None:
                    coverage += 1
        return coverage

    def _all_covered(self):
        for row in self.grid:
            for cell in row:
                if cell is None:
                    return False
        return True

    def visualize_grid(self):
        fig, ax = plt.subplots()
        self.selected_towers = []
        self.path_lines = []

        def onclick(event):
            ix, iy = event.xdata, event.ydata
            if ix is None or iy is None:
                return
            x, y = int(ix), int(iy)

            if 0 <= x < self.n and 0 <= y < self.m:
                if isinstance(self.grid[x][y], DefaultBlock) and self.grid[x][y].type == 't':
                    self.selected_towers.append((x, y))

                    if len(self.selected_towers) == 2:
                        for line in self.path_lines:
                            line.remove()
                        self.path_lines.clear()
                        fig.canvas.draw()

                        start, end = self.selected_towers
                        graph = self._create_graph()
                        path = self._bfs(graph, start, end)

                        print("Path found:", path)

                        if path is not None and len(path) > 1:
                            self._draw_path(ax, path)
                            fig.canvas.draw()
                        else:
                            print("No path")

                        self.selected_towers = []

        fig.canvas.mpl_connect('button_press_event', onclick)

        for y in range(self.m)[::-1]:
            for x in range(self.n):
                cell = self.grid[x][y]
                if cell is not None:
                    color = cell.color
                    type = cell.type
                    plot_x, plot_y = x, y
                    if type == "t":
                        circle = patches.Circle((plot_x + 0.5, plot_y + 0.5), 0.4, edgecolor='black', facecolor=color)
                        ax.add_patch(circle)
                    else:
                        rect = patches.Rectangle((plot_x, plot_y), 1, 1, edgecolor='black', facecolor=color)
                        ax.add_patch(rect)

        plt.xlim([0, self.n])
        plt.ylim([0, self.m])
        ax.set_xticks(range(self.n))
        ax.set_yticks(range(self.m)[::-1])
        plt.grid(which='major', axis='both', linestyle='-', color='k', linewidth=1)
        plt.show()

    def _draw_path(self, ax, path):
        if path:
            for i in range(len(path) - 1):
                start = path[i]
                end = path[i + 1]
                line = ax.plot([start[0] + 0.5, end[0] + 0.5], [start[1] + 0.5, end[1] + 0.5], color="blue", linewidth=2)
                self.path_lines.append(line[0])

    def _create_graph(self):
        graph = {}
        for x in range(self.n):
            for y in range(self.m):
                if isinstance(self.grid[x][y], DefaultBlock) and self.grid[x][y].type == 't':
                    graph[(x, y)] = self._get_adjacent_towers(x, y)

        return graph

    def _get_adjacent_towers(self, x, y):
        adjacent = []
        for i in range(self.n):
            for j in range(self.m):
                if (i, j) != (x, y) and isinstance(self.grid[i][j], DefaultBlock) and self.grid[i][j].type == 't':
                    range1 = [(x - self.range_r, y - self.range_r), (x + self.range_r, y + self.range_r)]
                    range2 = [(i - self.range_r, j - self.range_r), (i + self.range_r, j + self.range_r)]
                    if not (range1[1][0] < range2[0][0] or
                            range1[0][0] > range2[1][0] or
                            range1[1][1] < range2[0][1] or
                            range1[0][1] > range2[1][1]):
                        adjacent.append((i, j))
        return adjacent

    @staticmethod
    def _bfs(graph, start, end):
        if start == end:
            return [start]

        visited = set()
        queue = deque([[start]])

        while queue:
            path = queue.popleft()
            node = path[-1]

            if node not in visited:
                visited.add(node)

                for adjacent in graph.get(node, []):
                    if adjacent not in visited:
                        new_path = list(path)
                        new_path.append(adjacent)

                        if adjacent == end:
                            return new_path

                        queue.append(new_path)

        return None

    @staticmethod
    def _calculate_blocks(occupancy_percentage, total_blocks, round_up):
        if round_up:
            return math.ceil((occupancy_percentage * total_blocks) / 100)
        else:
            return (occupancy_percentage * total_blocks) // 100


city_grid = CityGrid(40, 20, 30, range_r=5)
city_grid.greedy_optimization()
city_grid.visualize_grid()