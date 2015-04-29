import ConfigParser
import subprocess
import sys
import time
import os
from thread import start_new_thread, allocate_lock
from multiprocessing import Pool, Process, Queue
from Queue import Empty
from ConfigParser import SafeConfigParser

#-----------------------------------------------------------------------------
#--returns sim time and # of cycles for a given simulation summary file
def getResult(path):
        parser = SafeConfigParser()
        parser.read(path)
        res = {}
        res[0] = parser.get(' Evergreen ', 'Instructions')
        res[1] = parser.get(' Evergreen ', 'Cycles')
        return res

#-----------------------------------------------------------------------------
#--compares simTime and/or cycles with the given summary files result
#--if given simTime is larger, returns false
def goForward(simtime,cycles,path):
        res1 = getResult(path)
        cycles1 = res1[0]
        sim_time1 = res1[1]
        if cycles1 < cycles:
                return false
        return true

#-----------------------------------------------------------------------------
#--computes Delta
#def computeDelta(path):
        res1 = getResult(path)
        cycles1 = res1[0]
        delta = cycles1*0.05
        return delta
        
#-----------------------------------------------------------------------------
#--creates config file based on given parameters
def create_config_file(path,dcu,nsc,nrg,ral,wfs,mwg,mwf,sch,lds):
        conf_file = open(path,'w')

        parser = ConfigParser.SafeConfigParser()

        parser.add_section('Device')
        parser.set('Device', 'Frequency', "700")
        parser.set('Device', 'NumComputeUnits', str(dcu))
        parser.set('Device', 'NumStreamCores', str(nsc))
        parser.set('Device', 'NumRegisters', str(nrg))
        parser.set('Device', 'RegisterAllocSize', "32")
        parser.set('Device', 'RegisterAllocGranularity', str(ral))
        parser.set('Device', 'WavefrontSize', str(wfs))
        parser.set('Device', 'MaxWorkGroupsPerComputeUnit', str(mwg))
        parser.set('Device', 'MaxWavefrontsPerComputeUnit', str(mwf))
        parser.set('Device', 'SchedulingPolicy', str(sch))

        parser.add_section('LocalMemory')
        parser.set('LocalMemory', 'Size', str(lds))
        parser.set('LocalMemory', 'AllocSize', "1024")
        parser.set('LocalMemory', 'BlockSize', "256")
        parser.set('LocalMemory', 'Latency', "2")
        parser.set('LocalMemory', 'Ports', "2")

        parser.add_section('CFEngine')
        parser.set('CFEngine', 'InstructionMemoryLatency', "2")

        parser.add_section('ALUEngine')
        parser.set('ALUEngine', 'InstructionMemoryLatency', "2")
        parser.set('ALUEngine', 'FetchQueueSize', "64")
        parser.set('ALUEngine', 'ProcessingElementLatency', "4")

        parser.add_section('TEXEngine')
        parser.set('TEXEngine', 'InstructionMemoryLatency', "2")
        parser.set('TEXEngine', 'FetchQueueSize', "32")
        parser.set('TEXEngine', 'LoadQueueSize', "8")

        parser.write(conf_file)

#-----------------------------------------------------------------------------
#--creates m2s simulation for given configuration and parameters
def run_simulation(benchmark,sim_id):
        cmd_m2s =""
        if benchmark == 1:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/BinarySearch/BinarySearch --load BinarySearch_Kernels.bin -q "
        if benchmark == 2:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/BinomialOption/BinomialOption --load BinomialOption_Kernels.bin -q "
        if benchmark == 3:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/BitonicSort/BitonicSort --load BitonicSort_Kernels.bin -q "
        if benchmark == 4:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/BlackScholes/BlackScholes --load BlackScholes_Kernels.bin -q "
        if benchmark == 5:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/DCT/DCT --load DCT_Kernels.bin -q "
        if benchmark == 6:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/DwtHaar1D/DwtHaar1D --load DwtHaar1D_Kernels.bin -q "
        if benchmark == 7:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/SobelFilter/SobelFilter --load SobelFilter_Kernels.bin -q "
        if benchmark == 8:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/FastWalshTransform/FastWalshTransform --load FastWalshTransform_Kernels.bin -q "
        if benchmark == 9:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/PrefixSum/PrefixSum --load PrefixSum_Kernels.bin -q "
        if benchmark == 10:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/MatrixTranspose/MatrixTranspose --load MatrixTranspose_Kernels.bin -q "
        if benchmark == 12:
                cmd_m2s = "m2s --evg-sim detailed --evg-report report_log"+sim_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
	#cmd_m2s = "m2s --evg-sim detailed --evg-calc "+sim_id+" --evg-report report_log"+rep_id+".txt"+" --evg-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/AMDAPP-2.5/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q -x "+ str(size_X) +" -y "+str(size_Y)+" -b "+str(block_size)
        print "##########################################################"
        print "simulation #"+sim_id
        f = open("summary"+sim_id+".txt", "w")
        p = subprocess.Popen(cmd_m2s, shell=True, stderr=subprocess.PIPE)
        while True:
                out = p.stderr.read(1)
                if out == '' and p.poll() != None:
                        break
                if out != '':
                        f.write(out)
                        f.flush()
        f.close()
#-----------------------------------------------------------------------------
#--creates processes
def do_work(q1,q2):
        
        while True:
                try:
                        sim_id = q2.get(block=False)
                        benchmark = q1.get(block=False)
                        time.sleep(.5)
                        run_simulation(benchmark,sim_id)
                        time.sleep(.5)
                except Empty:
                        break

#-----------------------------------------------------------------------------
#--main
if __name__ == "__main__":
        start_time =time.time()
        path = "/afs/nd.edu/user29/hsumerka/cse60321/project/v2/m2sconf.conf"
        
        dev_NumComputeUnits = [40] #[1,5,10,15,20,40]
        num_sc = [1,4,8,16,32,64]
        num_reg = [4096,8192,16384]
        reg_alloc = ["Wavefront","WorkGroup"]
        wf_size = [16,32,64]
        max_wg_pcu = [1,4,8]
        max_wf_pcu = [32]
        sched = ["RoundRobin","Greedy"]
        lds_sizes = [32768,65536,131072]
        for a in dev_NumComputeUnits:
                for b in num_sc:
                        for c in num_reg: 
                                for d in reg_alloc:
                                        for e in wf_size:
                                                for f in max_wg_pcu: 
                                                        for g in max_wf_pcu:
                                                                for h in sched:
                                                                        for j in lds_sizes:
                                                                                dcu = a
                                                                                nsc = b
                                                                                nrg = c
                                                                                ral = d
                                                                                wfs = e
                                                                                mwg = f
                                                                                mwf = g
                                                                                sch = h
                                                                                lds = j
                                                                                create_config_file(path,dcu,nsc,nrg,ral,wfs,mwg,mwf,sch,lds)
                                                                                benchmarks =  [1,2,3,4,5,6,7,8,9,10,11,12]
                                                                                work_queue1 = Queue()
                                                                                work_queue2 = Queue()
                                                                                for z in benchmarks:
                                                                                        sim_id = str(a)+"_"+str(b)+"_"+str(c)+"_"+str(d)+"_"+str(e)+"_"+str(f)+"_"+str(g)+"_"+str(h)+"_"+str(j)+"_"+str(z)
                                                                                        work_queue2.put(sim_id)
                                                                                        work_queue1.put(z)
                                                                                procs = 10
                                                                                processes = [Process(target=do_work, args=(work_queue1,work_queue2)) for r in xrange(procs)]
                                                                                for p in processes:
                                                                                        p.start()
                                                                                for p in processes:
                                                                                        p.join()
        res_dict = {}
        for a in dev_NumComputeUnits:
                for b in num_sc:
                        for c in num_reg: 
                                for d in reg_alloc:
                                        for e in wf_size:
                                                for f in max_wg_pcu: 
                                                        for g in max_wf_pcu:
                                                                for h in sched:
                                                                        for j in lds_sizes:
                                                                                benchmarks = [1,2,3,4,5,6,7,8,9,10,11,12]
                                                                                for z in benchmarks:
                                                                                        sim_id = str(a)+"_"+str(b)+"_"+str(c)+"_"+str(d)+"_"+str(e)+"_"+str(f)+"_"+str(g)+"_"+str(h)+"_"+str(j)+"_"+str(z)
                                                                                        path = "/afs/nd.edu/user29/hsumerka/cse60321/project/v2/"+"summary"+sim_id+".txt"
                                                                                        try:
                                                                                                sum = getResult(path)
                                                                                                cycles_gen = sum[0]
                                                                                                cycles_si = sum[1]
                                                                                                print sim_id
                                                                                                print cycles_gen
                                                                                                print cycles_si
                                                                                                res_dict.setdefault(sim_id, [])
                                                                                                res_dict[sim_id].append(cycles_gen)
                                                                                                res_dict[sim_id].append(cycles_si)
                                                                                        except:
                                                                                                print sim_id
        print(res_dict.keys())
        print(res_dict.values())
        print("--- %s seconds ---" % (time.time() - start_time))

