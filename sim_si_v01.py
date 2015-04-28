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
	res[0] = parser.get(' General ', 'Cycles')
	res[1] = parser.get(' SouthernIslands ', 'Cycles')
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
def create_config_file(path,dev_NumComputeUnits,cu_NumWavefrontPools,cu_NumVectorRegisters,cu_NumScalarRegisters,cu_MaxWorkGroupsPerWavefrontPool,cu_MaxWavefrontsPerWavefrontPool,lds_Size):
	conf_file = open(path,'w')

	parser = ConfigParser.SafeConfigParser()

	parser.add_section('Device')
	parser.set('Device', 'NumComputeUnits', str(dev_NumComputeUnits))

	parser.add_section('ComputeUnit')
	parser.set('ComputeUnit', 'NumWavefrontPools', str(cu_NumWavefrontPools))
	parser.set('ComputeUnit', 'NumVectorRegisters', str(cu_NumVectorRegisters))
	parser.set('ComputeUnit', 'NumScalarRegisters', str(cu_NumScalarRegisters))
	parser.set('ComputeUnit', 'MaxWorkGroupsPerWavefrontPool', str(cu_MaxWorkGroupsPerWavefrontPool))
	parser.set('ComputeUnit', 'MaxWavefrontsPerWavefrontPool', str(cu_MaxWavefrontsPerWavefrontPool))

	parser.add_section('FrontEnd')
	parser.set('FrontEnd', 'FetchLatency', '5')
	parser.set('FrontEnd', 'FetchWidth', '4')
	parser.set('FrontEnd', 'FetchBufferSize', '10')
	parser.set('FrontEnd', 'IssueLatency', '1')
	parser.set('FrontEnd', 'IssueWidth', '5')
	parser.set('FrontEnd', 'MaxInstIssuedPerType', '1')

	parser.add_section('SIMDUnit')
	parser.set('SIMDUnit', 'NumSIMDLanes', '16')
	parser.set('SIMDUnit', 'Width', '1')
	parser.set('SIMDUnit', 'IssueBufferSize', '1')
	parser.set('SIMDUnit', 'DecodeLatency', '1')
	parser.set('SIMDUnit', 'DecodeBufferSize', '1')
	parser.set('SIMDUnit', 'ReadExecWriteLatency', '8')
	parser.set('SIMDUnit', 'ReadExecWriteBufferSize', '2')

	parser.add_section('ScalarUnit')
	parser.set('ScalarUnit', 'Width', '1')
	parser.set('ScalarUnit', 'IssueBufferSize', '1')
	parser.set('ScalarUnit', 'DecodeLatency', '1')
	parser.set('ScalarUnit', 'DecodeBufferSize', '1')
	parser.set('ScalarUnit', 'ReadLatency', '1')
	parser.set('ScalarUnit', 'ReadBufferSize', '1')
	parser.set('ScalarUnit', 'ALULatency', '1')
	parser.set('ScalarUnit', 'ExecBufferSize', '16')
	parser.set('ScalarUnit', 'WriteLatency', '1')
	parser.set('ScalarUnit', 'WriteBufferSize', '1')

	parser.add_section('BranchUnit')
	parser.set('BranchUnit', 'Width', '1')
	parser.set('BranchUnit', 'IssueBufferSize', '1')
	parser.set('BranchUnit', 'DecodeLatency', '1')
	parser.set('BranchUnit', 'DecodeBufferSize', '1')
	parser.set('BranchUnit', 'ReadLatency', '1')
	parser.set('BranchUnit', 'ReadBufferSize', '1')
	parser.set('BranchUnit', 'ExecLatency', '1')
	parser.set('BranchUnit', 'ExecBufferSize', '1')
	parser.set('BranchUnit', 'WriteLatency', '1')
	parser.set('BranchUnit', 'WriteBufferSize', '1')

	parser.add_section('LDSUnit')
	parser.set('LDSUnit', 'Width', '1')
	parser.set('LDSUnit', 'IssueBufferSize', '1')
	parser.set('LDSUnit', 'DecodeLatency', '1')
	parser.set('LDSUnit', 'DecodeBufferSize', '1')
	parser.set('LDSUnit', 'ReadLatency', '1')
	parser.set('LDSUnit', 'ReadBufferSize', '1')
	parser.set('LDSUnit', 'MaxInflightMem', '32')
	parser.set('LDSUnit', 'WriteLatency', '1')
	parser.set('LDSUnit', 'WriteBufferSize', '1')

	parser.add_section('VectorMemUnit')
	parser.set('VectorMemUnit', 'Width', '1')
	parser.set('VectorMemUnit', 'IssueBufferSize', '1')
	parser.set('VectorMemUnit', 'DecodeLatency', '1')
	parser.set('VectorMemUnit', 'DecodeBufferSize', '1')
	parser.set('VectorMemUnit', 'ReadLatency', '1')
	parser.set('VectorMemUnit', 'ReadBufferSize', '1')
	parser.set('VectorMemUnit', 'MaxInflightMem', '32')
	parser.set('VectorMemUnit', 'WriteLatency', '1')
	parser.set('VectorMemUnit', 'WriteBufferSize', '1')

	parser.add_section('LocalDataShare')
	parser.set('LocalDataShare', 'Size', str(lds_Size))
	parser.set('LocalDataShare', 'AllocSize', '64')
	parser.set('LocalDataShare', 'BlockSize', '64')
	parser.set('LocalDataShare', 'Latency', '2')
	parser.set('LocalDataShare', 'Ports', '2')

	parser.write(conf_file)

#-----------------------------------------------------------------------------
#--creates m2s simulation for given configuration and parameters
def run_simulation(benchmark,sim_id):
	cmd_m2s =""
	if benchmark == 1:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/BinarySearch/BinarySearch --load BinarySearch_Kernels.bin -q "
        if benchmark == 2:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/BinomialOption/BinomialOption --load BinomialOption_Kernels.bin -q "      
        if benchmark == 3:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/BitonicSort/BitonicSort --load BitonicSort_Kernels.bin -q "
        if benchmark == 4:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/BlackScholes/BlackScholes --load BlackScholes_Kernels.bin -q "
        if benchmark == 5:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/DCT/DCT --load DCT_Kernels.bin -q "
        if benchmark == 6:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/DwtHaar1D/DwtHaar1D --load DwtHaar1D_Kernels.bin -q "
        if benchmark == 7:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/EigenValue/EigenValue --load EigenValue_Kernels.bin -q "
        if benchmark == 8:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/FastWalshTransform/FastWalshTransform --load FastWalshTransform_Kernels.bin -q "
        if benchmark == 9:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/FFT/FFT --load FFT_Kernels.bin -q "
        if benchmark == 10:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
        if benchmark == 12:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
        if benchmark == 13:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
        if benchmark == 14:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
        if benchmark == 15:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
        if benchmark == 16:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
        if benchmark == 17:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
        if benchmark == 18:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
        if benchmark == 19:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
        if benchmark == 20:
                cmd_m2s = "m2s --si-sim detailed --si-report report_log"+sim_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q "
	#cmd_m2s = "m2s --si-sim detailed --si-report report_log"+rep_id+".txt"+" --si-config m2sconf.conf /afs/nd.edu/user29/hsumerka/cse60321/m2s-bench-amdapp-2.5-si/MatrixMultiplication/MatrixMultiplication --load MatrixMultiplication_Kernels.bin -q -x "+ str(size_X) +" -y "+str(size_Y)+" -b "+str(block_size)
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
	path = "/afs/nd.edu/user29/hsumerka/cse60321/project/v1/m2sconf.conf"
        
	dev_NumComputeUnits = [8,16,32,64,96]
        cu_NumWavefrontPools = [1,2,4,8,16]
        cu_NumVectorRegisters = 65536
        cu_NumScalarRegisters = 2048
 	cu_MaxWorkGroupsPerWavefrontPool = 10
        cu_MaxWavefrontsPerWavefrontPool = 10
       	lds_sizes = [32768,65536,131072]
	for m in dev_NumComputeUnits:
                for n in cu_NumWavefrontPools:
			for k in lds_sizes: 
				dev_cu = m
				cu_pools = n
				lds_size = k
				create_config_file(path,dev_cu,cu_pools,cu_NumVectorRegisters,cu_NumScalarRegisters,cu_MaxWorkGroupsPerWavefrontPool,cu_MaxWavefrontsPerWavefrontPool,lds_size)
				benchmarks =  [1,2,3,4,5,6,7,8,9,10]
				work_queue1 = Queue()
				work_queue2 = Queue()
				for z in benchmarks:
					sim_id = str(m)+"_"+str(n)+"_"+str(k)+"_"+str(z)
					work_queue2.put(sim_id)
					work_queue1.put(z)
				procs = 10
				processes = [Process(target=do_work, args=(work_queue1,work_queue2)) for r in xrange(procs)]
				for p in processes:
					p.start()
				for p in processes:
					p.join()
	res_dict = {}
	for m in dev_NumComputeUnits:
                for n in cu_NumWavefrontPools:
			for k in lds_sizes:
				benchmarks = [1,2,3,4,5,6,7,8,9,10]
                        	for z in benchmarks:
					sim_id = str(m)+"_"+str(n)+"_"+str(k)+"_"+str(z)
					path = "/afs/nd.edu/user29/hsumerka/cse60321/project/v1/"+"summary"+sim_id+".txt"
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
