'''
    USAGE

    python Main.py noOFClasses noOfFilesForClass0 file0class0.txt file1class0.txt noOfFilesForClass1 file0class1.txt file1class1.txt noOfFilesToTest testfile1.txt testfile2.txt

    ex:
    python Main.py 2 2 trainA.txt trainAA.txt 3 trainB.txt trainBB.txt trainBBB.txt 2 testA testB


'''

import sys
import numpy as np
import keras

SEQUENCE_LENGTH = 1000


def fileRead(fileName,linesToRemove=4,leftColToRemove=1,rightColToRemove=3):
    file  = open(fileName, 'r')
    fullText=file.read()
    lines=fullText.split('\n')
    for x in range(linesToRemove):
        lines.pop(0)

    ar=[]
    for x in range(len(lines)):
        temp=[]
        fields=lines[x].split(",")
        for xx in range(len(fields)):
            fields[xx]=fields[xx].strip()

        for y in range(leftColToRemove,len(fields)-rightColToRemove):
            temp.append(float(fields[y]))
        if len(temp)==0:
            continue
        ar.append(temp)
        sys.stdout.flush()

    npar=np.zeros((len(ar), len(ar[0])))
    for i in range(len(ar)):
        for j in range(len(ar[0])):
            npar[i][j] = ar[i][j]
    print("Finished reading file "+fileName+" and returned a matrix: "+str(npar.transpose().shape))
    return npar.transpose()


def rnn_model1(NO_CLASSES,NO_CHANNELS):
    from keras.models import Sequential
    from keras.layers import LSTM,Dense,Softmax
    model=Sequential()
    model.add(LSTM(100,input_shape=(SEQUENCE_LENGTH,NO_CHANNELS)))
    model.add(Dense(NO_CLASSES))
    model.add(Softmax())
    return model

def rnnFit(Xtrain,YTrain,NO_CLASSES):
    Xnew=np.ndarray((0))
    Ynew=np.ndarray((0))
    for f in range(len(Xtrain)):

        startPoints = []
        startPoint = np.random.randint(0, SEQUENCE_LENGTH)

        while startPoint+SEQUENCE_LENGTH < Xtrain[f].shape[1]:
            startPoints.append(startPoint)
            startPoint+=np.random.randint(0,SEQUENCE_LENGTH)

        Xtemp = np.ndarray((len(startPoints), SEQUENCE_LENGTH, Xtrain[0].shape[0]))
        Ytemp = np.ndarray(len(startPoints),dtype=np.int32)


        for seqNum in range(Xtemp.shape[0]):
            for timeStamp in range(SEQUENCE_LENGTH):
                for channel in range(Xtemp.shape[2]):
                    Xtemp[seqNum,timeStamp,channel]=Xtrain[f][channel,startPoints[seqNum]+timeStamp]
            Ytemp[seqNum]=Ytrain[f]


        if f==0:
            Xnew=Xtemp
            Ynew=Ytemp
        else:
            print("Concatnating",Xnew.shape,Xtemp.shape)
            Xnew=np.concatenate((Xnew,Xtemp))
            Ynew = np.concatenate((Ynew, Ytemp))

    Ynew=keras.utils.to_categorical(Ynew, np.max(Ynew) + 1)
    #Now the training dataset Xnew,Ynew is ready

    model=rnn_model1(NO_CLASSES,Xnew.shape[2])
    model.compile(optimizer="adam",loss="mean_squared_error")
    model.summary()

    print("Fitting for shapes: ",Xnew.shape,Ynew.shape)
    model.fit(Xnew,Ynew)

    return model

def rnnPredict(model,X):


    startPoints = []
    startPoint = np.random.randint(0, SEQUENCE_LENGTH)

    while startPoint + SEQUENCE_LENGTH < X.shape[1]:
        startPoints.append(startPoint)
        startPoint += np.random.randint(0, SEQUENCE_LENGTH)

    Xtemp = np.ndarray((len(startPoints), SEQUENCE_LENGTH, X.shape[0]))

    for seqNum in range(Xtemp.shape[0]):
        for timeStamp in range(SEQUENCE_LENGTH):
            for channel in range(Xtemp.shape[2]):
                Xtemp[seqNum, timeStamp, channel] = X[channel, startPoints[seqNum] + timeStamp]

    Y=model.predict()

    print("The result is",Y)




if __name__== "__main__":
    Xtrain=[]
    Ytrain=[]
    NO_CLASSES=int(sys.argv[1])
    ALGORITHM=sys.argv[2]
    argvIndex=3
    FILES_PER_CLASS=np.zeros(NO_CLASSES,dtype=np.int32)
    for classNo in range(NO_CLASSES):
        FILES_PER_CLASS[classNo]=int(sys.argv[argvIndex])
        argvIndex+=1

        for trainFileIndex in range(FILES_PER_CLASS[classNo]):
            fileNameToRead=sys.argv[argvIndex]
            argvIndex+=1

            Xtrain.append(fileRead(fileNameToRead))
            Ytrain.append(classNo)


    if ALGORITHM=="rnn":
        rnnModel=rnnFit(Xtrain,Ytrain,NO_CLASSES)

        FILES_TO_PREDICT=int(sys.argv[argvIndex])
        argvIndex+=1

        for predictFileIndex in range(FILES_TO_PREDICT):
            fileNameToRead = sys.argv[argvIndex]
            argvIndex += 1

            Xtest=fileRead(fileNameToRead)
            rnnPredict(rnnModel,Xtest)







