# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 13:09:55 2023

@author: USER
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 18:24:24 2021

@author: USER
"""


import time as time
import os as os
import pandas as pd
import numpy as np
import sys
import math
import matplotlib.pyplot as plt
import random
os.chdir(os.path.abspath(os.path.dirname(__file__)))
def MaxGauss(Mean,Std,Recur):
    Result=-np.inf
    if Recur >0:
        Temp=np.random.normal(Mean,Std,Recur)
        Result=max(Temp)
    return Result
def MinGauss(Mean,Std,Recur):
    Result=np.inf
    if Recur >0:
        Temp=np.random.normal(Mean,Std,Recur)
        Result=min(Temp)
    return Result
def ConvertListFloatToListInt(Fl):

    Test=Fl

    Fl =[(x+1 if (x%1*100 <=random.randint(1,99)) and (x%1*100 !=0) else x) for x in Test]
    FL=[int(Fl) for Fl in Fl]
    return FL

os.chdir(os.path.abspath(os.path.dirname(__file__)))
#############WHAT DO U WANT TO DO ?
def CalculPointDeVie(DF):
    DF['PVMax']=np.random.normal(5,abs(5/10),(len(DF)))
    x = len(DF[DF.Type=='Soldat'])
    if x!=0:
        DF.loc[DF['Type']=='Soldat']['PVMax']=np.random.normal(6,abs(6/10),x)
    x=len(DF[(DF.Type=='Esclave')|(DF.Type=='Indien')])
    if x != 0:
        DF[(DF.Type=='Esclave')|(DF.Type=='Indien')]['PVMax']=np.random.normal(5.5,abs(5.5/10),x)
    DF[DF['PVMax']<5]['PVMax']=5
    DF[DF['PVMax'] > 8]['PVMax'] = 8
    DF['PVMax'] =ConvertListFloatToListInt(DF['PVMax'])
    return DF['PVMax']
def Save(TempDF,Name):
    TempDF.to_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252", index= False)
def Generate(Nb,Type,Name,Bonus):
    Text=""
    Pond = pd.read_csv("ListeProf.csv", sep=";", decimal=",", encoding="cp1252")
    ColNotComp=['Salaire','Employeur']  ###Liste des colonnes du fichier qui ne sont pas des compétences
    Ponds = Pond[Pond['Type']==Type]

    Equipe=pd.DataFrame(Ponds)
    Equipage=pd.DataFrame()
    for h in range(Nb):
        for k in Pond.columns[1:70]:
            if k not in ColNotComp:
                Equipe[k]=(Compute(Ponds[k]))
        Equipage=Equipage._append(Equipe)
    #Equipage.set_index("Type")
    Equipage["Nom"]=""
    Equipage["Maladie"]=0
    Equipage['Attitude']=0
    Equipage['Groupe']=""
    Equipage['Pirate']=1
    Equipage=Score(Equipage)
    Equipage['Attitude']=np.random.normal(50,abs(50/10),(len(Equipage)))
    Equipage['Attitude']=ConvertListFloatToListInt(Equipage['Attitude'])

    Equipage['KillCount']=0
    Equips,Temp=Pirate(Equipage,Bonus)
    for k in Ponds.columns:
        Equipage[k + "_exp"] = 0
    Equipage['PVMax']=CalculPointDeVie(Equipage)
    Equipage['PV']=Equipage['PVMax']
    Equipage.to_csv("Colonie/"+Name+"_COLONIE.csv",sep=";",decimal=",",encoding="cp1252")
    Text=Text+Temp+"\n"
    Text=Text+"Le groupe a été genere dans le fichier "+Name+".csv \n"
    print("Le groupe a été genere dans le fichier "+Name+".csv")
    return Text
def Compute(Prof):
    Base=random.choice(range(365))+1
    Metier=random.choice(range(10))+1
    if Base<190:
        Val=0
    elif Base<310:
        Val=1
    elif Base<355:
        Val=2
    else:
        Val=3
    if Metier<=2:
        Bonus=1
    elif Metier<=6:
        Bonus=2
    elif Metier<=8:
        Bonus=3
    else:
        Bonus=4
    Res=Val+Prof.iloc[0]*Bonus
    Rest=Res % 1

    if Rest>0:
        Tes=random.choice(range(10))+1
        if Tes>Res:
            Res=Res.astype(int)
        else:
            Res=Res.astype(int)+1
        
    return int(Res)

def LancerDe(col):
    ActCourte=0
    ActLongue=0
    Total=0
    Success = 0
    NbCrit=0
    NbEchec=0
    NbSimple=0
    NbDouble=0
    NbTriple=0
    if col == 0:
        Test = random.choice(range(12))+1
        if Test > 9:
            Success = -1
        elif Test == 1:
            Success = 2
        elif Test <= 5:
            Success = 1
    elif col > 0:
        for h in range(col):
            Test = random.choice(range(10))+1
            if Test == 1:
                if Success == -1:
                    Success = 0
                Success = Success + 2
            elif Test <= 5:
                if Success == -1:
                    Success = 0
                Success = Success + 1
            elif Test > 9 and Success < 1:
                Success = -1
    ActCourte = 4 - Success + ActCourte
    ActLongue = 7 - Success + ActLongue
    if Success == -1:
        NbCrit += 1
    if Success == 0:
        NbEchec += 1
    if Success == 1:
        NbSimple += 1
    if Success == 2:
        NbDouble += 1
    if Success > 2:
        NbTriple += 1

    Total = Total + Success
    Text="La personne a effectue "+str(Total)+ " succes et un total de "+str(ActCourte)+" actions courtes et de"+str(ActLongue)+ " actions longues"
    return Total,Text
def Recrute(Nb,Type,Name,Bonus):
    Pond=pd.read_csv("ListeProf.csv",sep=";",decimal=",",encoding="cp1252")
    Ponds = Pond[Pond['Type'] == Type]
    Equipe=pd.DataFrame(Ponds)
    Equipe.head=Pond.columns
    Equips=pd.DataFrame()
    
    Equipage=pd.read_csv("Colonie/"+Name+"_COLONIE.csv",sep=";",decimal=",",encoding="cp1252",index_col=0)
    for h in range(Nb):
        for k in Pond.columns:
            
            Equipe[k]=(Compute(Ponds[k]))
        
        Equips=Equips._append(Equipe)
    Equips,Temp=Pirate(Equips,Bonus)
    Equipage=Equipage._append(Equips)
    Equipage["Nom"] = ""
    Equipage["Maladie"] = 0
    Equipage['Attitude'] = 0
    Equipage['Groupe'] = ""
    Equipage['Pirate'] = 1
    Equipage = Score(Equipage)
    Equipage['PVMax']=CalculPointDeVie(Equipage)
    Equipage['PV'] = Equipage['PVMax']
    Equipage['KillCount']=0
    Equipage['Attitude'] = np.random.normal(50, abs(50 / 10), (len(Equipage)))
    Equipage['Attitude'] = ConvertListFloatToListInt(Equipage['Attitude'])
    for k in Ponds.columns:
        Equipage[k + "_exp"] = 0
    Text=Temp
    Equipage.to_csv("Colonie/"+Name+"_COLONIE.csv",sep=";",decimal=",",encoding="cp1252")
    return Text
def Test(Comp,Name,Bonus):
    TempDF=pd.read_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252")
    Success=0
    ActCourte=0
    ActLongue=0

    Total=0
    NbCrit=0
    NbEchec=0
    NbSimple=0
    NbDouble=0
    NbTriple=0
    for col in TempDF[Comp]:
        Success=0
        if col==0:
            Test=random.choice(range(12))+1
            if Test>9:
                Success=-1
            elif Test==1:
                if Bonus<-4:
                    Success=0
                else:
                    Success=2
            elif Test<=5+Bonus:
                Success=1
        elif col>0:
            for h in range(col):
                Test=random.choice(range(10))+1
                if Test==1:
                    if Success==-1:
                        Success=0
                    Success=Success+2
                elif Test<=5+Bonus:
                    if Success==-1:
                        Success=0
                    Success=Success+1
                elif Test>9 and Success<1:
                    Success=-1

        ActCourte=4-Success+ActCourte
        ActLongue=7-Success+ActLongue
        if Success==-1:
            NbCrit+=1
        if Success==0:
            NbEchec+=1
        if Success==1:
            NbSimple+=1
        if Success==2:
            NbDouble+=1
        if Success>2:
            NbTriple+=1
        Total=Total+Success
    Text="Le groupe a effectue "+str(NbCrit)+ " echec critique en "+Comp+"\n"+"Le groupe a effectue "+str(NbEchec)+ " echec simple en "+Comp+"\n"+"Le groupe a effectue "+str(NbSimple)+ " reussite mitigé en "+Comp+"\n"+"Le groupe a effectue "+str(NbDouble)+ " reussite double en "+Comp+"\n"+"Le groupe a effectue "+str(NbTriple)+ " triple reussite ou plus en "+Comp+"\n"+"Pour un total de "+str(ActCourte)+" actions courtes "+Comp+" pour une moyenne de "+str(ActCourte/len(TempDF))+"\n"+"Pour un total de "+str(ActLongue)+" actions longues "+Comp+" pour une moyenne de "+str(ActLongue/len(TempDF))+"\n"
    return Total,Text
                
def Score(TempDF):
    Capi=['Balistique','Connaissances nautiques','Hydrographie','Navigation','Tactique','MeneurHommes']
    Second=['Connaissances nautiques','MeneurHommes','Pratique nautique','Tactique']
    Canonnier=['Balistique','Connaissances nautiques','MeneurHommes','Recharge','Pointage','Tactique']
    MaitreEquipage=['Connaissances nautiques','Enseignement','Intimidation','Pratique nautique','MainsNue']
    MaitreCanonnier=['Pointage','Recharge','Connaissances nautiques','Enseignement','Intimidation','Pratique nautique']
    QuartierMaitre=['MeneurHommes','Connaissances nautiques','Droit','Empathie','Enseignement','Pratique nautique','Persuasion','Timonerie']
    Score=0
    for k in TempDF.columns.values.tolist():
        if ((k!='Nom') and ( k!='Groupe') and (k!="Maladie") and (k!="Attitude")and (k!="Pirate")and (k!="Role")and (k!="Type") and (k!="Salaire") and (k!="Employeur")):

            Score=Score+TempDF[k]
            TempDF['Score']=Score/len(TempDF.columns)
    Score=0
    for k in Capi:
        Score=Score+TempDF[k]
        TempDF['Capi']=Score/len(Capi)
    Score=0
    Score=0
    for k in Second:
        Score=Score+TempDF[k]
        TempDF['Second']=Score/len(Second)
    Score=0
    Score=0
    for k in Canonnier:
        Score=Score+TempDF[k]
        TempDF['Canonnier']=Score/len(Canonnier)
    Score=0
    for k in MaitreEquipage:
        Score=Score+TempDF[k]
        TempDF['MaitreEquipage']=Score/len(MaitreEquipage)
    Score=0
    for k in MaitreCanonnier:
        Score=Score+TempDF[k]
        TempDF['MaitreCanonnier']=Score/len(MaitreCanonnier)
    Score=0
    for k in QuartierMaitre:
        Score=Score+TempDF[k]
        TempDF['QuartierMaitre']=Score/len(QuartierMaitre)
    Score=0
    TempDF=Role(TempDF)
    return TempDF
def Groupe(Seuil,Comp,Name,NouvName):
    TempDF=pd.read_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252")

    TempDF['Groupe'] = TempDF['Groupe'].fillna("")
    TempDF.loc[(TempDF[Comp] >= Seuil) & (~TempDF['Groupe'].str.contains(NouvName)),'Groupe']=TempDF['Groupe']+","+NouvName
    Resp = TempDF[TempDF[Comp] >= Seuil]
    Save(TempDF,Name)
    return Resp.to_string()
def Tues(Morts,Equipage):
    TempDF=pd.read_csv("Colonie/"+Equipage,sep=";",decimal=",",encoding="cp1252")
    arr_indices_top_drop = random.choices(TempDF.index, k=Morts)
    TempDF.drop(index=arr_indices_top_drop)
    TempDF.to_csv("Colonie/"+Equipage,sep=";",decimal=",",encoding="cp1252")
    return Morts
def Degats(Name,Comp,Bonus):
    TempDF=pd.read_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252")
    Degats=0
    if Comp!="":
        Len=len(TempDF.index)
        Degats,Text=Test(Comp,Name,Bonus)
    return Degats

def DegatsMesure(Name, Comp,Bonus):
    TempDF = pd.read_csv("Colonie/" + Name, sep=";", decimal=",", encoding="cp1252")
    if Comp != "":
        Len = len(TempDF.index)
        Degats, Text = Test(Comp, Name,Bonus)
        DegMoy = Degats / Len
        print(Degats)
        print(DegMoy)
        Valeur = 0.9925 * np.exp(0.2298*(Len - 9.9721 + 2 * DegMoy))
        print(Valeur)
    else:
        Valeur = 0

    # Mesure=9.802*np.exp(0.2278*Valeur)/10
    return Valeur
def Perte(Degats,Name):
    TempDF=pd.read_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252")
    Mort=0
    for k in range(Degats):
        Extract = TempDF.sample()
        Extract['PV']-=1
        TempDF.loc[Extract.index,'PV']=int(Extract['PV'].iloc[0])
        if (int(Extract['PV'].iloc[0])<1) and (len(TempDF)>0):   ##Si l'element selectonne a 0 PV, on le supprime du groupe
            TempDF = TempDF.drop(Extract.index)
            Mort+=1


        elif len(TempDF)<1:
            TempDF=pd.DataFrame()
            print(Name+" a été decime")
    TempDF.to_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252")

    return Mort

def SelectRandom(Name, Nb):
    TempDF=pd.read_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252")
    Res=pd.DataFrame()
    for k in range(Nb):
        Res=Res._append(TempDF.sample())
    Text=Res.to_string()
    return Text

def BatailleTerrestre(Name1,Comp1,Name2,Comp2,Bonus1,Bonus2):
    Text=""
    Armee1=pd.read_csv("Colonie/"+Name1,sep=";",decimal=",",encoding="cp1252")
    Armee2=pd.read_csv("Colonie/"+Name2,sep=";",decimal=",",encoding="cp1252")
    Text=Text+Name1+ " a encore "+str(len(Armee1))+" disponibles au combat \n"
    Text = Text + Name2 + " a encore " + str(len(Armee2)) + " disponibles au combat \n"
    print(Name1+ " a encore "+str(len(Armee1))+" disponibles au combat")
    print(Name2+ " a encore "+str(len(Armee2))+" disponibles au combat")
    Perte1=0
    Perte2=0
    Degat1=Degats(Name1,Comp1,Bonus1)
    Degat2=Degats(Name2,Comp2,Bonus2)
    print(Degat1)
    print(Degat2)
    if(len(Armee1)>0):
        Perte1=Perte(Degat2,Name1)
        Text=Text+Attitude(Name1,-Perte1/len(Armee1)*50)[1]
    else:
        print(Armee1+" a ete decimee")
    if(len(Armee2)>0):
        Perte2=Perte(Degat1,Name2)
        Text=Attitude(Name2, -Perte2/len(Armee2)*50)[1]
    else:
        print(Armee2+" a ete decimee")
    print(Name1+" a perdu "+str(Perte1)+" hommes")
    
    print(Name2+" a perdu "+str(Perte2)+" hommes")
    return Text
def Recrutement(TempDF,Name,Nb,Bonus):
    for k in range(Nb):
        TempDF.append()
    TempDF=Score(TempDF)
    Equipage=Pirate(TempDF,Bonus)
    TempDF.to_csv("Colonie/"+Name+"_COLONIE.csv",sep=";",decimal=",",encoding="cp1252", index= False)
###Exemple, cl
def NommerRandom(Nom,Name):
    TempDF=pd.read_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252")
    dfupdate=TempDF.sample()
    dfupdate["Nom"]=Nom
    TempDF.update(dfupdate)
    TempDF.to_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252", index= False)
def Role(TempDF):
    TempDF['Role']=''
    Roles=['Capi','Second','MaitreEquipage','MaitreCanonnier','Canonnier','QuartierMaitre']
    for k in Roles:
        
        TempDF.loc[(TempDF[k]==TempDF[k].max()) & (TempDF['Role']==''),'Role']=k
    return TempDF

def Attitude(Name, Modif):

    TempDF = pd.read_csv("Colonie/"+Name, sep=";", decimal=",", encoding="cp1252")
    TempDF['Attitude']+=np.random.normal(Modif,abs(Modif/10),(len(TempDF)))
    Texts=""
    TempDF['Attitude']=ConvertListFloatToListInt(TempDF['Attitude'])
    Seuils=[25,10,0,-10,-25,-50]
    for k in Seuils:
        if(len(TempDF[TempDF['Attitude']<k])>0):
           Text=Texts+"Dans l'equipage "+Name+" "+str(len(TempDF[TempDF['Attitude']<k])) +" ont une loyaute inférieure a "+str(k)+" sur "+str(len(TempDF))+" hommes disponibles \n"
           print(Text)
    TempDF.to_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252",index=False)
    return TempDF,Texts
def Maladie(Name,Seuil,De,CompMedecin):
    TempDF=pd.read_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252")

    TempDF.loc[np.random.choice(range(De),size=len(TempDF))<=Seuil-1,'Maladie']=1

    if De>10000:
        TempDF['Maladie']=0

    TempDF.to_csv("Colonie/"+Name,sep=";",decimal=",",encoding="cp1252", index= False)
def AttributeExp(Name,Comp,Exp):
    TempDF = pd.read_csv("Colonie/"+Name, sep=";", decimal=",", encoding="cp1252")
    TempDF[Comp+"_exp"]+=int(Exp)
    TempDF.loc[(TempDF[Comp+"_exp"]>0)&(TempDF[Comp]<0)|(TempDF[Comp+"_exp"]>TempDF[Comp]*TempDF[Comp]), Comp] += 1


    TempDF.loc[(TempDF[Comp+"_exp"]>0)&(TempDF[Comp]<0)|(TempDF[Comp+"_exp"]>TempDF[Comp]*TempDF[Comp]), Comp+"_exp"] = 0
    TempDF.to_csv("Colonie/"+Name, sep=";", decimal=",", encoding="cp1252", index=False)
    return "Les expériences ont été sauvegardées dans le fichier "+Name+".csv"
def Pirate(TempDF,Symp):
    Text=""
    TempDF["Pirate"]=0
    if Symp==1:
        OK=1
        TempDF.loc[np.random.choice(range(10),size=len(TempDF))>10,'Pirate']=-1
        TempDF.loc[np.random.choice(range(10),size=len(TempDF))<=5,'Pirate']=1
        TempDF.loc[np.random.choice(range(10),size=len(TempDF))<=1,'Pirate']=2
    if Symp==0:
        TempDF.loc[np.random.choice(range(10),size=len(TempDF))>5,'Pirate']=-1
        TempDF.loc[np.random.choice(range(10),size=len(TempDF))<=2,'Pirate']=1
        TempDF.loc[np.random.choice(range(10),size=len(TempDF))<=0,'Pirate']=2
    if Symp==-1:
        TempDF.loc[np.random.choice(range(10),size=len(TempDF))>0,'Pirate']=-1
        TempDF.loc[np.random.choice(range(10),size=len(TempDF))<=-1,'Pirate']=1
        TempDF.loc[np.random.choice(range(10),size=len(TempDF))<=-1,'Pirate']=2
    Size1=len(TempDF[TempDF["Pirate"]==-1])
    Size2=len(TempDF[TempDF["Pirate"]==0])
    Size3=len(TempDF[TempDF["Pirate"]==1])
    Size4=len(TempDF[TempDF["Pirate"]==2])
    Text=Text+str(Size1)+" membres sont prets à dénoncer des agissements pirates \n"+ str(Size2)+" membres sont neutres envers des agissements pirates \n" +str(Size3)+" membres sont prets à aider des agissements pirates \n"+str(Size4)+" membres sont prets à sauver des agissements pirates \n"
    print(Text)
    return TempDF,Text
def AfficheColonne(Name,Comp):
    TempDF = pd.read_csv("Colonie/"+Name, sep=";", decimal=",", encoding='cp1252')
    print(TempDF[Comp].value_counts())
    return TempDF[Comp].value_counts().to_string()
def RecruteEquipage(TypeRecrutant,EquipageRecrutant,EquipageRecrute,SuccesRecrutement):
    Text=""
    EquipageRecruteDF=pd.read_csv("Colonie/"+EquipageRecrute,sep=";",decimal=",",encoding="cp1252")
    EquipageRecrutantDF = pd.read_csv("Colonie/" + EquipageRecrutant, sep=";", decimal=",", encoding="cp1252")
    if TypeRecrutant=='Pirate':
        EquipageRecruteDF['Pirate']=EquipageRecruteDF['Pirate']*(1+SuccesRecrutement/10)  ####En fonction du succes de recrutement, le ralliement à la cause pirate de l'equipage recruté va etre modifié
        EquipageRecruteDF['Pirate']=ConvertListFloatToListInt(EquipageRecruteDF['Pirate'])
        Text = Text + str(len(EquipageRecruteDF[EquipageRecruteDF['Pirate'] < 0])) + " sont prets à dénoncer l'equipage pirate \n"
        PersonneRecrute=EquipageRecruteDF[EquipageRecruteDF['Pirate'] > 1]       ###Les personnes ralliés à la cause pirate rejoignent l'equipage

        Text = Text + str(len(PersonneRecrute)) + " sont prets à rejoindre l'equipage \n"
        EquipageRecrutantDF=pd.concat([EquipageRecrutantDF,PersonneRecrute])
        EquipageRecrutantDF.to_csv("Colonie/"+EquipageRecrutant,sep=";",decimal=",",encoding="cp1252")

    return Text

def SoinsEquipage(CompMedecine,CompChrirugie,Equipage):
    TempDF=pd.read_csv('Equipage/'+Equipage,sep=";",decimal=",",encoding='cp1252')
    TempDF['PV']=TempDF['PVMax']
    TempDF['PV']-=1
    TempDF.to_csv('Equipage/'+Equipage,sep=";",decimal=",",encoding='cp1252')
    return TempDF