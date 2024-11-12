# Practica 1 Socket_TCP

## Descripción General

Este programa es un servidor TCP multihilo en el que agentes simulan una tarea colaborativa. Un agente (Agente 1) realiza una solicitud de ayuda después de una espera simulada de 10 segundos, mientras que los otros agentes (Agente 2, 3, etc.) esperan para responder. Los agentes tienen un 30% de probabilidad de responder a la solicitud de ayuda. Si suficientes agentes responden (al menos 2), la solicitud se satisface y el juego termina. Si no, la solicitud expira después de un límite de tiempo.

## Cómo Funciona

1. El servidor escucha en el puerto 9999.
2. Los clientes (agentes) se conectan al servidor, y a cada uno se le asigna un rol.
3. El Agente 1 (el primero que se conecta) envía una solicitud de ayuda después de esperar 10 segundos simulados (para que de tiempo a que los otros se conecten).
4. Los demás agentes conectados esperan a que el primero envie el mensaje de ayuda y una vez realizado, envian una respuesta al mensaje de ayuda (positiva en un 30% de las ocasiones).
5. El Agente 1 espera 10 segundos a que los otros le respondan, si en ese tiempo hay 2 respuestas con ayuda, se termina el programa. Contrariamente, si en ese tiempo no se reciben las dos respuestas positivas, el programa termina.

## Cómo Ejecutar

1. Se arranca una terminal y se accede al directorio que contiene el programa.
2. Lanzamos el programa con: python3 p1_robles.py
3. Abrimos otra terminal y lanzamos el siguiente comando: nc localhost 9999 (Agente 1, que envia el mensaje de ayuda).
4. Abrimos más terminales con el comando anterior (Otros Agentes que envian respuestas).
5. En la primera terminal (la que ha lanzado el programa) tendremos los logs con la simulación del juego.

## Notas

- Cuando el Agente 1 pide ayuda, como los otros agentes ya están conectados, se ejecutan todas las respuestas a la vez (puesto que los otros agentes han estado esperando a la petición de ayuda), esto puede conducir a que los prints no estén ordenados (debido a concurrencia). Aún así, esto no afecta al resultado del programa.
- Los agentes se van desconectando a medida que envian respuestas a la ayuda (envian una respuesta y se desconectan), excepto el Agente 1, que se desconecta cuando recibe la ayuda suficiente o cuando se cumple el timeout.
