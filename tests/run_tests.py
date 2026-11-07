"""Dos casos: funcional HTTP y rendimiento secuencial local. BD aislada."""
import contextlib, datetime, io, json, os, platform, sys, tempfile, threading, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app

root=Path(__file__).resolve().parents[1]
evidence=root/'evidencias'; evidence.mkdir(exist_ok=True)
def main():
    checks=[]; samples=[]; log=io.StringIO()
    with tempfile.TemporaryDirectory(dir=root) as tmp, contextlib.redirect_stderr(log):
        app.DB=str(Path(tmp)/'test.sqlite3')
        server=app.make_server(0)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        def request(path,data=None):
            req=Request(base+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
            try:
                with urlopen(req,timeout=5) as response:return response.status,json.load(response)
            except HTTPError as err:return err.code,json.load(err)
        def check(name,actual,expected):
            checks.append({'verificacion':name,'esperado':expected,'obtenido':actual,'aprobado':actual==expected})
        # CP01: flujo funcional y límites del stock.
        check('Alta producto',request('/api/productos',{'sku':'P001','nombre':'Teclado','cantidad':10})[0],201)
        check('SKU duplicado',request('/api/productos',{'sku':'P001','nombre':'Teclado','cantidad':10})[0],409)
        check('Entrada +5',request('/api/movimientos',{'sku':'P001','cambio':5})[0],200)
        check('Salida -4',request('/api/movimientos',{'sku':'P001','cambio':-4})[0],200)
        check('Rechazo salida -12',request('/api/movimientos',{'sku':'P001','cambio':-12})[0],400)
        check('Stock final conservado',request('/api/productos')[1],[{'sku':'P001','nombre':'Teclado','cantidad':11}])
        check('Rechazo cantidad negativa',request('/api/productos',{'sku':'P002','nombre':'Ratón','cantidad':-1})[0],400)
        check('Rechazo cantidad decimal',request('/api/productos',{'sku':'P002','nombre':'Ratón','cantidad':1.5})[0],400)
        # CP02: 10 calentamientos; 200 GET medidos, un cliente, sin concurrencia.
        for _ in range(10):request('/api/productos')
        for i in range(200):
            start=time.perf_counter(); status,data=request('/api/productos'); ms=(time.perf_counter()-start)*1000
            samples.append({'iteracion':i+1,'ms':ms,'status':status,'correcto':status==200 and data==[{'sku':'P001','nombre':'Teclado','cantidad':11}]})
        server.shutdown();server.server_close();thread.join()
    ordered=sorted(x['ms'] for x in samples);p95=ordered[189]
    result={'fecha':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entorno':platform.platform(),'python':sys.version,'cp01':checks,'cp02':{'n':200,'calentamiento':10,'clientes':1,'umbral_p95_ms':100,'p95_ms':p95,'media_ms':sum(x['ms'] for x in samples)/200,'correctas':sum(x['correcto'] for x in samples),'aprobado':p95<=100 and all(x['correcto'] for x in samples)},'metricas':{'verificaciones_funcionales_pct':sum(x['aprobado'] for x in checks)/len(checks)*100,'p95_ms':p95,'respuestas_correctas_pct':sum(x['correcto'] for x in samples)/200*100},'muestras':samples}
    (evidence/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (evidence/'servidor.log').write_text(log.getvalue(),encoding='utf-8')
    summary='CP01 funcional: '+str(sum(x['aprobado'] for x in checks))+'/'+str(len(checks))+' verificaciones\nCP02 rendimiento: '+str(result['cp02'])+'\nMétricas: '+str(result['metricas'])
    print(summary);(evidence/'ejecucion.txt').write_text(summary,encoding='utf-8')
    assert all(x['aprobado'] for x in checks) and result['cp02']['aprobado']
if __name__=='__main__':main()
