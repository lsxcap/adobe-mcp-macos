import {createInterface} from 'node:readline';
import {execFile} from 'node:child_process';
const app=process.env.ILLUSTRATOR_APP_PATH;
if (!app) throw new Error('ILLUSTRATOR_APP_PATH is required');
const quote=s=>'"'+s.replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\n/g,'\\n').replace(/\r/g,'\\r')+'"';
for await (const line of createInterface({input:process.stdin})) {
 const req=JSON.parse(line);const script=Buffer.from(req.script,'base64').toString('utf8');
 const source='tell application '+quote(app)+'\n do javascript '+quote(script)+'\nend tell';
 await new Promise(resolve=>execFile('/usr/bin/osascript',['-e',source],{maxBuffer:32*1024*1024},(e,out)=>{console.log(JSON.stringify(e?{id:req.id,ok:false,error:e.message,executionState:'unknown'}:{id:req.id,ok:true,result:out.trim()}));resolve();}));
}
