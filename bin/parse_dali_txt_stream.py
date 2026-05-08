import sys
from collections import namedtuple
import numpy as np

def parse_dali_txt_stream(stream,verbose=False):
    """returns a list of named tuples:
        cd1,zscore,rmsd,lali,nres,pide [Dali stats]
        qstarts, sstarts, lengths [vectors encoding alignment]
        u, t [vectors encoding rotation and translation matrices]

    Summary block must be present. Missing alignment or translation-rotation block yield empty vectors.
    """
    #print("parse_dali_txt",filename,os.path.isfile(filename),file=sys.stderr)
    # summary block
    summary=[]
    cd1='Query'
    # Structural equivalences block
    qstarts=[]
    sstarts=[]
    lengths=[]
    # Translation-rotation matrices block
    u=[]
    t=[]
    # parse file
    if True:
        # capture Query
        for line in stream:
            if line.startswith('# Query:'):
                cd1=line[9:14]
                break
        # skip headers
        for line in stream:
            if line.startswith('# No:'): break
        # summary block
        hdr=''
        for x in stream:
            if x.startswith('#'):
                hdr=x
                break
            x=x.rstrip()
            if len(x)==0: continue
#43713:  ppub-A  2.0 15.7  108   420    6   MOLECULE: CHROMOSOMAL REPLICATION INITIATOR PROTEIN DNAA;
            tmp=x.split(':')
            line=tmp[1]
            cd2=line[2:6]+line[7]
            zscore=float(line[9:14])
            rmsd=float(line[14:19])
            lali=int(line[19:24])
            nres=int(line[24:30])
            pide=int(line[31:35])
            summary.append([cd2,zscore,rmsd,lali,nres,pide])
        if hdr.startswith('# Pairwise'):
            for x in stream:
                if x.startswith('#'): break
        # store alignment block in buffer for parsing later
        #  2: 2nrm-A 101m-A     1 -  47 <=>    6 -  52   (ALA    2  - GLN   48  <=> GLY    5  - THR   51 )
        #  2: 2nrm-A 101m-A    48 - 115 <=>   54 - 121   (ALA   49  - GLY  116  <=> ALA   53  - PRO  120 )
        #  2: 2nrm-A 101m-A   116 - 146 <=>  124 - 154   (LEU  117  - GLY  147  <=> PHE  123  - GLY  153 )
        # group lines by common id
        q={}
        s={}
        l={}
        lista=[]
        for line in stream:
            if line.startswith('# Translation-rotation matrices'): break
            line=line.rstrip()
            if line=='': continue
            id=line[0:20]
            if id not in q:
                q[id]=[]
                s[id]=[]
                l[id]=[]
                lista.append(id)
            x=line.split(':')
            line=x[1]
            #print('||'.join([line[16:20],line[22:26],line[31:35]]))
            qfrom=int(line[16:20])
            qto=int(line[22:26])
            sfrom=int(line[31:35])
            q[id].append(qfrom)
            s[id].append(sfrom)
            l[id].append(qto-qfrom+1)
        # write csv to qstarts[], sstarts[], lengths[] keeping input order
        for id in lista:
            qstarts=list(q.values())
            sstarts=list(s.values())
            lengths=list(l.values())
        # u3b block
        #matrix  "2nrm-A 101m-A  U(1,.)  -0.753961  0.567882 -0.330232           27.728849"
        #matrix  "2nrm-A 101m-A  U(2,.)   0.240092 -0.229709 -0.943180            1.541300"
        #matrix  "2nrm-A 101m-A  U(3,.)  -0.611473 -0.790407  0.036848           40.543331"
        # read three lines at a time
        while True:
            line1=stream.readline().rstrip()
            if not line1: break
            if len(line1)==0: continue
            line2=stream.readline()
            line3=stream.readline()
            u.append([
                float(line1[33:42]), float(line1[42:52]), float(line1[52:62]),
                float(line2[33:42]), float(line2[42:52]), float(line2[52:62]),
                float(line3[33:42]), float(line3[42:52]), float(line3[52:62])])
            t.append([float(line1[62:82]), float(line2[62:82]), float(line3[62:82])])
    # merge lists horizontally
    n=len(summary)
    if len(qstarts)<n:
        qstarts=[[]]*n
        sstarts=[[]]*n
        lengths=[[]]*n
    if len(u)<n:
        u=[[]]*n
        t=[[]]*n
    Row=namedtuple('Dali','cd2 zscore rmsd lali nres pide qstarts sstarts lengths u t')
    return( cd1, [ Row._make([summary[i][0],summary[i][1],summary[i][2],summary[i][3],summary[i][4],summary[i][5],np.array(qstarts[i],dtype=int),np.array(sstarts[i],dtype=int),np.array(lengths[i],dtype=int),u[i],t[i]]) for i in range(0,len(summary)) ] )

cd1,x=parse_dali_txt_stream(sys.stdin)
# remove newlines from string representation of numpy arrays (qstarts, etc.)
for row in x: print("\t".join([cd1]+list(map(str,row))+['.','.']).replace('\n',''))

