const fs=require('fs');const path=require('path');const {pathToFileURL}=require('url');
const {chromium}=require('C:/Users/23670/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const root=__dirname;const out=path.join(root,'交付');
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 const page=await browser.newPage({viewport:{width:1920,height:1250},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(out,'厄尔尼诺_自绘动态示意.html')).href);await page.evaluate(()=>document.fonts.ready);
 const checks=[];
 for(const [t,name] of [[0,'正常状态'],[6,'暖水东移'],[15,'厄尔尼诺状态']]){
  await page.evaluate(t=>window.setTime(t),t);
  await page.locator('#art').screenshot({path:path.join(out,`自绘图解_${name}.png`)});
  checks.push(await page.evaluate(()=>({caption:document.getElementById('caption').textContent,state:document.getElementById('stateLabel').textContent,warm:document.getElementById('warmLayer').getAttribute('d'),wind:document.getElementById('trade').getAttribute('d')})));
 }
 await page.click('#normal');await page.click('#play');await page.waitForTimeout(1200);
 const time=await page.evaluate(()=>Number(document.getElementById('timeline').value));if(time<8)throw new Error('Animation did not advance');
 await page.click('#play');await page.click('#el');
 if(errors.length)throw new Error(errors.join('\n'));
 fs.writeFileSync(path.join(root,'动态示意验证.json'),JSON.stringify({javascript_errors:errors,animation_advances:true,states:checks,own_vector_diagram:true,video_exported:false},null,2),'utf8');
 await browser.close();console.log('Dynamic diagram checked');
})().catch(e=>{console.error(e);process.exitCode=1});
