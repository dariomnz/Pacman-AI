def min_solution(maze, x = 0, y = 0, path = None):
    def try_next(x, y):
        ' Next position we can try '
        return [(a, b) for a, b in [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)] if 0 <= a < n and 0 <= b < m]

    n = len(maze)
    m = len(maze[0])
    
    if path is None:
        path = [(x, y)]         # Init path to current position

    # Reached destionation
    if x == n - 1 and y == m - 1:
        return path
    
    maze[x][y] = 1              # Mark current position so we won't use this cell in recursion
    
    # Recursively find shortest path
    shortest_path = None            
    for a, b in try_next(x, y):
        if not maze[a][b]:
            last_path = min_solution(maze, a, b, path + [(a, b)])  # Solution going to a, b next
            
            if not shortest_path:
                shortest_path = last_path        # Use since haven't found a path yet
            elif t_path and len(last_path) < len(shortest_path):
                shortest_path = last_path       # Use since path is shorter
     
    
    maze[x][y] = 0           # Unmark so we can use this cell
    
    return shortest_path


maze = [
      [0, 0, 1, 1],
      [1, 0, 0, 0],
      [1, 1, 1, 0]
    ]

t = min_solution(maze)
if t:
    print(f'Shortest path {t} has length {len(t)}')
else:
    print('Path not found')