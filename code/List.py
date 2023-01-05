import sys, random
from heapq import heappush, heappop, heapify




def evaluate(graph, p, time, priority_order):
    schedule = [[] for i in range(p)]
    child, parent = graph
    n = len(time)
    ls = priority_order
    done = [0] * n
    end_time = [-1] * n
    donect = 0
    heap = [(0, i) for i in range(p)]
    heapify(heap)
    while donect < n:
        # print "Heap is:",heap
        item = heappop(heap)
        tproc, proc = item
        lefttask = -1
        for task in ls:
            if done[task]:
                continue
            flag = True
            for par in parent[task]:
                if end_time[par] < 0 or end_time[par] > tproc:
                    flag = False
                    break
            if flag:
                lefttask = task
                break
        if lefttask != -1:
            heappush(heap, (tproc + time[lefttask], proc))
            schedule[proc].append(lefttask)
            donect += 1
            done[lefttask] = 1
            end_time[lefttask] = tproc + time[lefttask]
        else:
            tmp = [item]
            while heap and heap[0][0] == tproc:
                tmp.append(heappop(heap))
            new_time = heap[0][0]
            while tmp:
                heappush(heap, (new_time, (tmp.pop())[1]))
    mtime = max(elem[0] for elem in heap)
    # sanity_check(schedule,num_tasks)
    return mtime, schedule


def finish_time(graph, schedule, time):
    n = len(graph[0])
    parent = graph[1]
    pos = [(-1, -1) for i in range(n)]
    for i in range(len(schedule)):
        for j in range(len(schedule[i])):
            pos[schedule[i][j]] = (i, j)
    for elem in pos:
        assert elem != (-1, -1)

    time_tasks = [-1] * n
    for i in range(n):
        if time_tasks[i] == -1:
            S = []
            S.append(i)
            while S:
                task = S[-1]
                x, y = pos[task]
                ptask = schedule[x][y - 1] if y else -1
                if time_tasks[task] != -1:
                    S.pop()
                    min_par = max([time_tasks[par] for par in parent[task]] or [0])
                    minimum = min_par if y == 0 else max(min_par, time_tasks[ptask])
                    time_tasks[task] = time[task] + minimum
                else:
                    time_tasks[task] = 0
                    if y:
                        S.append(ptask)
                    for par in parent[task]:
                        if time_tasks[par] == -1 and par != ptask:
                            S.append(par)
    return max(time_tasks)


def swap(ls):
    newls = [elem for elem in ls]
    n = len(newls);
    i = random.randint(0, n - 1)
    j = random.randint(0, n - 1)
    newls[i], newls[j] = newls[j], newls[i]
    return newls


def sanity_check(schedule, num_tasks, res_time):
    sm = sum(len(processor) for processor in schedule)
    assert sm == num_tasks
    pos = [(-1, -1) for i in range(num_tasks)]
    for i in range(len(schedule)):
        for j in range(len(schedule[i])):
            pos[schedule[i][j]] = (i, j)
    for elem in pos:
        assert elem != (-1, -1)
    for proc in schedule:
        for i in range(0, len(proc)):
            task = proc[i]
            pari = graph[1][task]
            for j in range(i + 1, len(proc)):
                task2 = proc[j]
                assert task2 not in pari
    assert finish_time(graph, schedule, time) == res_time



with open(r'../data/rand0000.txt', 'r') as files:
    temp = list(map(int, files.readline().split(' ')))
    num_tasks = temp[0]
    num_edges = 0
    time = []
    num_proc = 4
    graph = [[] for i in range(num_tasks)], [[] for i in range(num_tasks)]
    for i in range(num_tasks):
        data = list(map(int, files.readline().split('         ')))
        time.append(data[1])
        for j in range(data[2]):
            father, child = data[3 + j] - 1, data[0] - 1
            if father == -1:
                continue
            num_edges += 1
            graph[0][father].append(child)
            graph[1][child].append(father)
files.close()

priority_order = [i for i in range(0, num_tasks)]
unstable = 1
result, bst_sch = evaluate(graph, num_proc, time, priority_order)
ct = 40 * num_tasks
while unstable:
    if not ct:
        unstable = 0
        break
    newls = swap(priority_order)
    new_res, cand_shd = evaluate(graph, num_proc, time, newls)
    if new_res < result:
        result = new_res
        priority_order = newls
        bst_sch = cand_shd
    else:
        ct -= 1
sanity_check(bst_sch, num_tasks, result)
print(result)
