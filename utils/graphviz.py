import os
from os import system
import time


def basicMBR_report(mbr, args):
    vizCode = """digraph {{

    node [ shape=none fontname=Helvetica ]

    n1 [ label = <
      <table>

         <tr>
         <td colspan="2" bgcolor="Yellow">[MBR] <br/> Size: {} Bytes <br/> Creation date: {} <br/> Signature: {} <br/>  Fit: {} </td>
         <td colspan="2" bgcolor="Green">[Partition1] <br/> Status: {} <br/> Type: {}<br/> Fit: {}<br/> Start: {} <br/>Size: {}<br/> Name: {}</td>
         <td colspan="2" bgcolor="Green">[Partition2] <br/> Status: {} <br/> Type: {}<br/> Fit: {}<br/> Start: {}<br/> Size: {}<br/> Name: {}</td>
         <td colspan="2" bgcolor="Green">[Partition3] <br/> Status: {} <br/> Type: {}<br/> Fit: {}<br/> Start: {}<br/> Size: {}<br/> Name: {}</td>
         <td colspan="2" bgcolor="Green">[Partition4] <br/> Status: {} <br/> Type: {}<br/> Fit: {}<br/> Start: {}<br/> Size: {}<br/> Name: {}</td>
         </tr>

      </table>
    > ]\n}}""".format(
        mbr.size, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mbr.creationDate)), mbr.signature,
        mbr.fit.decode('utf-8'),
        mbr.partition1.status.decode('utf-8'), mbr.partition1.type.decode('utf-8'),
        mbr.partition1.fit.decode('utf-8'), mbr.partition1.start, mbr.partition1.size,
        mbr.partition1.name.decode('utf-8'),
        mbr.partition2.status.decode('utf-8'), mbr.partition2.type.decode('utf-8'),
        mbr.partition2.fit.decode('utf-8'), mbr.partition2.start, mbr.partition2.size,
        mbr.partition2.name.decode('utf-8'),
        mbr.partition3.status.decode('utf-8'), mbr.partition3.type.decode('utf-8'),
        mbr.partition3.fit.decode('utf-8'), mbr.partition3.start, mbr.partition3.size,
        mbr.partition3.name.decode('utf-8'),
        mbr.partition4.status.decode('utf-8'), mbr.partition4.type.decode('utf-8'),
        mbr.partition4.fit.decode('utf-8'), mbr.partition4.start, mbr.partition4.size,
        mbr.partition4.name.decode('utf-8'))

    directory = os.path.dirname(args.path)
    os.makedirs(directory, exist_ok=True)

    filename = args.path.split('.')

    nuevo_archivo = open(filename[0] + '.dot', "w")
    nuevo_archivo.write(vizCode)
    nuevo_archivo.close()

    system("dot -Tpng " + f"{filename[0]}.dot" + " -o " + f"{filename[0]}.png")
    system('rm ' + f"{filename[0]}.dot")
