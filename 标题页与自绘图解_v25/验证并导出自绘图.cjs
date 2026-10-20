const fs=require('fs'),path=require('path'),vm=require('vm');
const sharp=require('C:/Users/23670/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=__dirname,out=path.join(root,'交付');
const html=fs.readFileSync(path.join(out,'厄尔尼诺_自绘动态示意.html'),'utf8');
const original=html.match(/<svg id="art"[\s\S]*?<\/svg>/)[0];const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const items={};for(const hit of html.matchAll(/id="([^"]+)"/g))items[hit[1]]={attrs:{},style:{},textContent:null,value:'0',setAttribute(k,v){this.attrs[k]=String(v)}};
const context={document:{getElementById:id=>items[id]},window:{},performance:{now:()=>0},requestAnimationFrame:()=>{}};vm.createContext(context);vm.runInContext(script,context);
function escaped(v){return String(v).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;')}
function svg(t){context.window.setTime(t);let art=original;
 for(const [id,el] of Object.entries(items)){
  const rx=new RegExp(`<([\\w]+)([^>]*\\bid="${id}"[^>]*)>`);
  art=art.replace(rx,(all,tag,attrs)=>{const closed=/\/$/.test(attrs);if(closed)attrs=attrs.slice(0,-1);for(const [k,v]of Object.entries(el.attrs)){const ar=new RegExp(`\\s${k}="[^"]*"`);if(ar.test(attrs))attrs=attrs.replace(ar,` ${k}="${escaped(v)}"`);else attrs+=` ${k}="${escaped(v)}"`}return `<${tag}${attrs}${closed?'/':''}>`});
  if(el.textContent!==null)art=art.replace(new RegExp(`(<text[^>]*id="${id}"[^>]*>)[^<]*(</text>)`),(all,a,z)=>a+escaped(el.textContent)+z);
 }
 return art.replace('<defs>','<style>text{font-family:Microsoft YaHei,Arial,sans-serif;fill:#244c60}</style><defs>');
}
(async()=>{
 const states=[];
 for(const [t,name]of [[0,'正常状态'],[6,'暖水东移'],[15,'厄尔尼诺状态']]){
  const art=svg(t);fs.writeFileSync(path.join(out,`自绘图解_${name}.svg`),art,'utf8');
  await sharp(Buffer.from(art)).resize(1920,1080).png().toFile(path.join(out,`自绘图解_${name}.png`));
  states.push({seconds:t,wind:items.trade.attrs.d,warm:items.warmLayer.attrs.d,cloud:items.cloud.attrs.transform,caption:items.caption.textContent});
 }
 if(states[0].warm===states[2].warm||states[0].cloud===states[2].cloud)throw Error('State unchanged');
 context.window.setTime(0);items.play.onclick();vm.runInContext('step(1200)',context);if(Number(items.timeline.value)<8)throw Error('Animation time did not advance');
 items.normal.onclick();if(items.stateLabel.textContent!=='正常状态')throw Error('Normal control failed');
 items.el.onclick();if(items.stateLabel.textContent!=='厄尔尼诺状态')throw Error('El Nino control failed');
 fs.writeFileSync(path.join(root,'动态示意验证.json'),JSON.stringify({state_math_and_controls:'PASS',states,rendered_static_svg_png:true,browser_visual_test:'Not completed: sandbox prevented headless browser launch',own_vector_diagram:true,video_exported:false},null,2),'utf8');console.log('State logic and native SVG previews verified');
})().catch(e=>{console.error(e);process.exitCode=1});
