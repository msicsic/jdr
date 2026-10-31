// Reproduction du build transmis par le joueur : navigateur et profil isolés.
// Même configuration FER_PUPPETEER_MODULE / FER_RAPIER_MODULE / FER_BROWSER
// que test-fer-assistance.cjs. FER_DIAGNOSTIC=1 écrit les traces sans assertions.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const http=require('node:http'),{once}=require('node:events');
const root=path.resolve(__dirname,'..');
const puppeteer=require(process.env.FER_PUPPETEER_MODULE||'puppeteer-core');
const source=fs.readFileSync(process.env.FER_HTML||path.join(root,'fer-et-flamme.html'),'utf8');
const html=source.replace('</script>',`
window.__ferTest={
 step(s){for(let i=0;i<Math.round(s*60);i++)boucle((dernier+1/60)*1000);},
 etat(){const v=vehicule;return {...__fer.etat(),av:v.body.angvel(),com:v.body.localCom(),
   inertie:v.inertie,altCible:v.altCible,xCible:v.xCible,
   couple:v.thrusters.reduce((s,t)=>s+(t.rx*t.force.y-t.ry*t.force.x)*t.forceN*v.facteur,0),
   hud:{vx:ui.vx.textContent,vy:ui.vy.textContent,alt:ui.alt.textContent,assiette:ui.angle.textContent}};}
};
</script>`);
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'fer-build-joueur.json'),'utf8'));
async function main(){
 const out=path.join(root,'artifacts','fer-stabilite');fs.mkdirSync(out,{recursive:true});
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);});
 server.listen(0,'127.0.0.1');await once(server,'listening');let browser;
 const resultats=[];
 try{
  browser=await puppeteer.launch({executablePath:process.env.FER_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu']});
  const page=await browser.newPage();await page.setViewport({width:1440,height:900});
  const erreurs=[];page.on('pageerror',e=>erreurs.push(e.message));
  await page.evaluateOnNewDocument(()=>{window.requestAnimationFrame=()=>0;});
  if(process.env.FER_RAPIER_MODULE){
   const body=fs.readFileSync(process.env.FER_RAPIER_MODULE,'utf8');await page.setRequestInterception(true);
   page.on('request',r=>r.url().includes('/rapier.mjs')?r.respond({status:200,contentType:'text/javascript',headers:{'Access-Control-Allow-Origin':'*'},body}):r.continue());
  }
  const ready=()=>page.waitForFunction('!!window.__ferTest',{timeout:15000,polling:100});
  await page.goto(`http://127.0.0.1:${server.address().port}/fer-et-flamme.html`);await ready();
  const step=s=>page.evaluate(s=>__ferTest.step(s),s),etat=()=>page.evaluate(()=>__ferTest.etat());
  const plans={joueur:fixture,decale:fixture.map(b=>({...b,col:b.col-3})),centreHaut:[...fixture,{type:'coeur',col:6,row:4,rot:0}]};
  for(const[nom,design]of Object.entries(plans)){
   await page.evaluate(design=>localStorage.setItem('fer-et-flamme.design.v2',JSON.stringify({design,selected:'poste',ghostRot:0})),design);
   for(let recharge=0;recharge<2;recharge++){
    await page.reload();await ready();assert.deepEqual(await page.evaluate(()=>__fer.design()),design);
    await page.evaluate(()=>{__fer.lancer();__fer.placer(-60,16);});await step(3);
    const hover=await etat();
    const episodes=[];
    for(const touche of ['d','a']){
     await page.evaluate(()=>__fer.placer(-35,16));await step(1);
     const trace=[];await page.keyboard.down(touche);
     for(let i=0;i<10;i++){await step(0.1);trace.push({phase:'acceleration',t:(i+1)/10,...await etat()});}
     await page.keyboard.up(touche);
     for(let i=0;i<80;i++){await step(0.1);trace.push({phase:'freinage',t:1+(i+1)/10,...await etat()});}
     const fin=await etat();episodes.push({touche,trace,fin});
     console.log(nom,recharge,touche,JSON.stringify({angleMax:Math.max(...trace.map(e=>Math.abs(e.angle))),avMax:Math.max(...trace.map(e=>Math.abs(e.av))),yMin:Math.min(...trace.map(e=>e.y)),yMax:Math.max(...trace.map(e=>e.y)),fin:{vx:fin.vx,vy:fin.vy,angle:fin.angle,y:fin.y}}));
    }
    await page.screenshot({path:path.join(out,`${nom}-${recharge}.png`)});
    resultats.push({nom,recharge,design,hover,episodes});
    fs.writeFileSync(path.join(out,process.env.FER_DIAGNOSTIC?'avant.json':'resultats.json'),JSON.stringify(resultats,null,2));
    if(!process.env.FER_DIAGNOSTIC){
     assert.ok(Math.abs(hover.angle)<0.04&&Math.abs(hover.vx)<0.1&&Math.abs(hover.vy)<0.2,nom+' stationnaire');
     for(const e of episodes){
      assert.ok(e.trace.every(p=>!p.sol&&!p.hs&&Math.abs(p.angle)<0.9),nom+' assiette maîtrisée');
      assert.ok(e.trace.every(p=>Math.abs(p.y-16)<1),nom+' altitude');
      assert.ok(Math.abs(e.fin.vx)<0.25&&Math.abs(e.fin.angle)<0.07,nom+' arrêt stable');
      assert.ok(Math.abs(parseFloat(e.fin.hud.vx)-e.fin.vx)<0.1,nom+' vitesse visible');
      assert.ok(Math.abs(parseFloat(e.fin.hud.alt)-e.fin.y)<0.1,nom+' altitude visible');
      assert.ok(Math.abs(parseFloat(e.fin.hud.assiette)-e.fin.angle*180/Math.PI)<1,nom+' assiette visible');
     }
    }
   }
  }
  if(!process.env.FER_DIAGNOSTIC){
   const reference=resultats.find(c=>c.nom==='joueur'&&c.recharge===0);
   for(const cas of resultats.filter(c=>c.nom==='joueur'||c.nom==='decale')){
    cas.episodes.forEach((episode,i)=>episode.trace.forEach((e,j)=>{
     const r=reference.episodes[i].trace[j];
     for(const champ of ['x','y','vx','vy','angle','av']){
      assert.ok(Math.abs(e[champ]-r[champ])<0.002,'recharge et déplacement grille invariants : '+champ);
     }
    }));
   }
   console.log('OK invariance du vol après recharge et déplacement dans la grille');
  }
  assert.deepEqual(erreurs,[]);
 }finally{if(browser)await browser.close();server.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
