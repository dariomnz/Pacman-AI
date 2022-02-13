import os,sys,threading,time

def prueba():
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l labAA1 -k 1 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l labAA2 -k 2 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l labAA3 -k 3 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l labAA4 -k 3 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l labAA5 -k 3 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l bigHunt -k 4 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l newmap -k 4 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l oneHunt -k 4 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l openClassic -k 4 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l openHunt -k 4 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l sixHunt -k 6 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l smallClassic -k 4 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l trappedClassic -k 4 -a epsilon=0.05,alpha=0")
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l layout_personal -k 4 -a epsilon=0.05,alpha=0")
def final():
    # random =  " -g RandomGhost"
    # append =  ""
    append =  " -g RandomGhost"
    for nombre,n_ghost in [
            ("labAA1","1"),
            ("labAA2","2"),
            ("labAA3","3"),
            ("labAA4","3"),
            ("labAA5","3"),
            ("20Hunt","4"),
            ("bigHunt","4"),
            ("capsuleClassic","4"),
            ("mediumClassic","4"),
            ("mimapa","4"),
            ("minimaxClassic","4"),
            ("newmap","4"),
            ("oneHunt","4"),
            ("openClassic","4"),
            ("openHunt","4"),
            # ("originalClassic","4"),
            ("sixHunt","6"),
            ("smallClassic","4"),
            ("smallHunt","4"),
            ("testClassic","4"),
            ("trappedClassic","4"),
            ("trickyClassic","4"),
            ("layout_personal","4")
            ]:
        command="python ./busters.py --frameTime 0 -p BasicAgentAA -l "+nombre+" -k "+n_ghost+append
        print(command)
        if os.system(command) == -1:
            return False
    return True

def final_perfe():
    for nombre,n_ghost in [
        
            ("labAA1","1"),
            ("labAA2","2"),
            ("labAA3","3"),
            ("labAA4","3"),
            ("labAA5","3"),
            ("20Hunt","4"),
            ("bigHunt","4"),
            ("capsuleClassic","4"),
            ("mediumClassic","4"),
            ("mimapa","4"),
            ("minimaxClassic","4"),
            ("newmap","4"),
            ("oneHunt","4"),
            ("openClassic","4"),
            ("openHunt","4"),
            # ("originalClassic","4"),
            ("sixHunt","6"),
            ("smallClassic","4"),
            ("smallHunt","4"),
            ("testClassic","4"),
            ("trappedClassic","4"),
            ("trickyClassic","4"),
            ("layout_personal","4")
            ]:
        for append in [" --quietTextGraphics"," --quietTextGraphics -g RandomGhost"]:
            command="python ./busters.py --frameTime 0 -p BasicAgentAA -l "+nombre+" -k "+n_ghost+append
            print(command)
            if os.system(command) == -1:
                return False
    return True

def entrenar(n_ejecucion):
    for epsilon in [0.3]:
        for x in range(3):
            for nombre,n_ghost in [
            ("labAA5","3"),
            ("labAA2","2"),
            ("labAA4","3"),
            ("labAA3","3"),
            ("oneHunt","4"),
            # ("bigHunt","4"),
            ("newmap","4"),
            ("openHunt","4"),
            ("openClassic","4"),
            # ("sixHunt","6"),
            ("capsuleClassic","4"),
            ("smallClassic","4"),
            ("trappedClassic","4"),
            ("layout_personal","4")
            ]:
                    print("thread: "+threading.current_thread().name+" entrenamiento: "+str(n_ejecucion[0])+" de epsilon: "+str(epsilon))
                    command = "python ./busters.py -p QLearningAgent --quietTextGraphics --frameTime 0 -l "+nombre+" -k "+n_ghost+" -a epsilon="+str(epsilon)+",tickLimit=1000,entrenamiento=1,alpha=0.1"
                    print(command)
                    os.system(command)
                    n_ejecucion[0] += 1  
                    time.sleep(0.01)  
        
def entrenar2(n_ejecucion):
    for epsilon in [0.3]:
            # with lock:
            for nombre,n_ghost in [
            # ("labAA5","3"),
            # ("labAA2","2"),
            # ("labAA4","3"),
            # ("labAA3","3"),
            # ("oneHunt","4"),
            # # # ("bigHunt","4"),
            # # ("newmap","4"),
            # ("openClassic","4"),
            # # ("sixHunt","6"),
            # ("capsuleClassic","4"),
            # ("smallClassic","4"),
            # ("trappedClassic","4"),
            # ("layout_personal","4"),
            ("openHunt","4"),
            # ("trickyClassic","4"),
            ]:
                for x in range(2):
                        print("thread: "+threading.current_thread().name+" entrenamiento: "+str(n_ejecucion[0])+" de epsilon: "+str(epsilon))
                        command = "python ./busters.py -p QLearningAgent --quietTextGraphics --frameTime 0 -l "+nombre+" -k "+n_ghost+" -a epsilon="+str(epsilon)+",tickLimit=1000,entrenamiento=1,alpha=0.1"
                        print(command)
                        os.system(command)
                        n_ejecucion[0] += 1  
                        time.sleep(0.01)  
if sys.argv[1] == "entrenar":
    start_time = time.time()
    os.system("copy .\qtable.ini.txt .\qtable.txt")
    n_ejecucion = [0]
    entrenar(n_ejecucion)
    elapsed_time = time.time() - start_time

    print("Entrenar time: %0.10f seconds." % elapsed_time)
    final()
elif sys.argv[1] == "entrenar_perfe":
    perfecto = False
    while(not perfecto):
        start_time = time.time()
        os.system("copy .\qtable.ini.txt .\qtable.txt")
        n_ejecucion = [0]
        entrenar2(n_ejecucion)
        elapsed_time = time.time() - start_time
    
        print("Entrenar time: %0.10f seconds." % elapsed_time)
        perfecto = final_perfe()
elif sys.argv[1] == "prueba":
    prueba()
elif sys.argv[1] == "final":
    final()
elif sys.argv[1] == "final_perfe":
    print(final_perfe())
else:
    os.system("python ./busters.py -p QLearningAgent --frameTime 0 -l "+sys.argv[1]+" -k "+sys.argv[2]+" -a epsilon=0.05,alpha=0")
