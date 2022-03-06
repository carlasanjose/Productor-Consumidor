#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 17:21:22 2022

@author: Lasjimenez
"""

from multiprocessing import Process
from multiprocessing import Semaphore, BoundedSemaphore
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
import random

#por ejemplo elijo que haya 3 productores y cada uno produzca 10 productos:
    
NPROD=3
N=10

def producer(storage,sem_empty,sem_nonempty,pid):
    v=0
    for i in range(N):
        print (f"{current_process().name} está produciendo")
        sleep(random.random()/3)
        v += random.randint(0,5)
        sem_empty[pid].acquire()
        storage[pid] = v
        sem_nonempty[pid].release()
        print (f"{current_process().name} ha producido {v}")

    
    #cuando ya se han producido los N productos:

    sem_empty[pid].acquire() #wait empty
    storage[pid]=-1
    sem_nonempty[pid].release() #signal nonEmpty 

    
    
def minimo(lista): #función auxiliar que calcula el minimo de una lista devolviendo el valor y 
                   #la posición que ocupa(teniendo en cuenta los valores que sean distintos de -1)
                   
    aux = 10000 #pongo 10000 para comparar, ya que no vamos a llegar a un numero tan alto
    indice=-1 #auxiliar para guardar aqui la posicion del mínimo
    for i in range(len(lista)):
        if lista[i] < aux and lista[i]!=-1:
            aux = lista[i]
            indice = i
    return aux, indice
    
    
    
def consumer(storage,sem_empty,sem_nonempty,lista):
    lista_aux=[-1]*NPROD #lista auxiliar para regular cuando acaban de producir todos los prodcutores

    for i in range(NPROD):
        sem_nonempty[i].acquire()
        
    while lista_aux != list(storage):
        minn, posicion = minimo(storage)
        lista.append(minn)
        print ('Consumidor está consumiendo', minn, 'del productor', posicion)
        sem_empty[posicion].release()
        sem_nonempty[posicion].acquire()
        
    #cuando todos han acabado de producir, ya no se mete en el bucle anterior
    
        
    print('Quedan en este orden consumidos los productos:', lista)
        
    
    
def main():
    lista=[] #aqui vamos a almacenar en orden los productos que va consumiendo el consumidor
    storage = Array('i', NPROD) 
    sem_empty=[] #lista de semaforos empty
    sem_nonempty=[] #lista de semaforos nonEmpty
    for i in range(NPROD):
        storage[i] = 0
        non_empty = Semaphore(0) 
        empty = BoundedSemaphore(1)
        sem_empty.append(empty)
        sem_nonempty.append(non_empty)
    print ("almacen inicial", storage[:])

    prodlst = [ Process(target=producer,
                        name=f'Productor_{i}',
                        args=(storage, sem_empty, sem_nonempty, i))
                for i in range(NPROD) ]

    cons = Process(target=consumer,
                      name="consumidor",
                      args=(storage, sem_empty,sem_nonempty,lista))

  
    #para poner en marcha los procesos:
        
    for p in prodlst:
         p.start()
    cons.start() 
    
    #con el join "esperan" a que vayan acabando todos los procesos
    
    for p in prodlst:
        p.join()
    cons.join()


if __name__ == '__main__':
    main()
