import sys,re,os.path
import numpy as np
import pandas as pd

def get_cd1(fn):
    "extract cd1 from DALI output file path/cd1.txt"
    # prepend cd1
    y = re.search(r"\w{5}.txt", fn)
    cd1=(y.group()[:5])
    return(cd1)

def dali_txt_to_df(filename,dat1,dat2,TARGET='DB',verbose=False):
    """returns Pandas dataframe 
        cd1,cd2,zscore,rmsd,lali,nres,pide [Dali stats]
        qstarts, sstarts, lengths [vectors encoding alignment]
        u, t [vectors encoding rotation and translation matrices]
        sbjct-sequence [sbjct protein's sequ record from .dat file]
        sbjct-dssp
        description [ sbjct protein's compnd record fromu .dat file]
        sequ-pileup
        dssp-pileup

    Summary block must be present. Missing alignment or translation-rotation block yield empty vectors.
    """
    cd1 = get_cd1(filename)
    querydata = read_DAT(dat1,cd1)
    #print("parse_dali_txt",filename,os.path.isfile(filename),file=sys.stderr)
    # summary block
    summary=[]
    # Structural equivalences block
    qstarts=[]
    sstarts=[]
    lengths=[]
    # Translation-rotation matrices block
    u=[]
    t=[]
    # parse file
    if os.path.isfile(filename):
      with open(filename,'r') as f:
        # skip headers
        for line in f:
            if line.startswith('# No:'): break
        # summary block
        hdr=''
        for x in f:
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
            # pileups
            x,nres2,dssp,sequ,desc=read_DAT(dat2,cd2)
            summary.append([cd2,zscore,rmsd,lali,nres,pide,sequ,dssp,desc])
        if hdr.startswith('# Pairwise'):
            for x in f:
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
        for line in f:
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
            line1=f.readline().rstrip()
            if not line1: break
            if len(line1)==0: continue
            line2=f.readline()
            line3=f.readline()
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
    # fetch sbjct sequence
    
    # prepend cd1
    y = re.search(r"\w{5}.txt", filename)
    cd1=(y.group()[:5])
    data = [ [ cd1, TARGET,summary[i][0],summary[i][1],summary[i][2],summary[i][3],summary[i][4],summary[i][5],summary[i][6],summary[i][7],summary[i][8],str(np.array(qstarts[i],dtype=int)),str(np.array(sstarts[i],dtype=int)),str(np.array(lengths[i],dtype=int)),str([i]),str(t[i]) ] for i in range(0,len(summary)) ] 
    # add Query data
    nres=querydata[1]
    queryrow = [ cd1, 'Query', cd1, '.', '0.0',nres,nres,'100',str(querydata[3]),str(querydata[2]),str(querydata[4]),'[ 1 ]','[ 1 ]',f'[ {nres} ]', '[ 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 ]','[0/0 0/0 0/0]' ]
    # vstack queryrow and data
    a_array=np.array(queryrow).reshape(1,-1)
    b_array=np.array(data)
    result = np.vstack([a_array,b_array])
    # return Pandasdf
    df = pd.DataFrame(result, columns=['query','database','sbjct','z-score','rmsd','ali-length','sbjct-length','seq-identity','sbjct-sequence','sbjct-dssp','description','qstarts','sstarts','lengths','rotation','translation' ])
    # generate pileups
#    nres=querydata[1] 
#    df['sequ-pileup'] = df.apply(lambda row: pileup(row['qstarts'], row['sstarts'], row['lengths'],row['sbjct-sequence'],nres), axis=1)
#    df['dssp-pileup'] = df.apply(lambda row: pileup(row['qstarts'], row['sstarts'], row['lengths'],row['sbjct-dssp'],nres), axis=1)
    return(df)

def read_DAT(datadir, cd2):
    """
    Extracts and returns DSSP, sequence, and compound information
    from a DALI .dat file.

    Parameters:
        datadir (str): Path to the directory containing .dat files.
        cd2 (str): Identifier prefix of the .dat file (without extension).

    Returns tuple:
        cd2 (str): echo input
        nres (int): length of sequence
        dssp (str): 3-state secondary structure (H = helix, E = sheet, L = loop)
        sequ (str): amino acid sequence
        description (str): COmPND record of PDB file
    """
    filepath = f"{datadir}/{cd2}.dat"
    dssp = sequ = description = ""
    with open(filepath, 'r') as fh:
        for line in fh:
            if not line.startswith('-'):
                continue
            if line[1:4] == 'acc':
                continue
            parts = line.split('"')
            key = line[1:7].strip()
            if key.startswith('sequ') and len(parts) > 1:
                # DSSP writes disulphide partners in lowercase -> revert to 'C'
                sequ = re.sub(r'[a-z]', 'C', parts[1].strip())
            elif key.startswith('dssp') and len(parts) > 1:
                dssp = parts[1].strip()
            elif key.startswith('compnd') and len(parts) > 1:
                compnd = parts[1].strip()
    return cd2, len(sequ), dssp, sequ, compnd

def pileup(qs,ss,le,txt,nres):
    "returns gapped pileup string"
    # convert strings  to int
    qstarts = list(map(int, str(qs).strip('[]').split()))
    sstarts = list(map(int, str(ss).strip('[]').split()))
    lengths = list(map(int, str(le).strip('[]').split()))
    #print("pileup",qstarts,sstarts,lengths,len(txt),nres,file=sys.stderr)
    res=['.']*(nres)
    lentext=len(txt)
    if qstarts is not None:
      for q,s,l in zip(qstarts,sstarts,lengths):
        for i in range(-1,l-1):
                if q+i>=nres: break
                if s+i>=lentext: break
                res[q+i]=txt[s+i]
    return("".join(res))

def add_pileup(df):
    # generate pileups
    df['sequ-pileup'] = df.apply(lambda row: pileup(row['qstarts'], row['sstarts'], row['lengths'],row['sbjct-sequence'],nres), axis=1)
    df['dssp-pileup'] = df.apply(lambda row: pileup(row['qstarts'], row['sstarts'], row['lengths'],row['sbjct-dssp'],nres), axis=1)
    return(df)

if __name__=="__main__":
    fn=sys.argv[1]
    dat1=sys.argv[2]
    dat2=sys.argv[3]
    TARGET=sys.argv[4]
    df=dali_txt_to_df(fn,dat1,dat2,TARGET=TARGET)
    # add_pileup(df)
    df.to_csv(sys.stdout, sep='\t', index=False)
