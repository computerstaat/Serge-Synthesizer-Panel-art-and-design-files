const M=JSON.parse(document.getElementById('man').textContent),HD=JSON.parse(document.getElementById('holes').textContent),D=96,MMI=25.4,cache={};let sel=[],uid=0;
const NS='http://www.w3.org/2000/svg',INK='http://www.inkscape.org/namespaces/inkscape';
const $=id=>document.getElementById(id);
function lib(){const q=$('q').value.toLowerCase(),er=$('era').value;$('lst').innerHTML='';
 M.forEach((m,i)=>{if(er&&m.e!==er)return;if(q&&!m.n.toLowerCase().includes(q))return;
  const d=document.createElement('div');d.className='it';d.title='Add '+m.n;
  d.innerHTML=(m.t?'<img loading="lazy" src="'+m.t+'" alt="">':'')+m.n+'<br><small>'+m.e+' · '+(+m.w).toFixed(2)+'"'+(m.k?'':' · no drill data')+'</small>';
  d.onclick=()=>{sel.push(i);draw()};$('lst').appendChild(d)})}
async function get(m){if(!cache[m.s]){const r=await fetch(m.s);cache[m.s]=await r.text()}return cache[m.s]}
const lab=g=>g.getAttribute('inkscape:label')||'';
function nest(txt,x,y,m,keep){const p='m'+(++uid)+'-';
 txt=txt.replace(/<\?xml[^>]*>/,'').replace(/<!DOCTYPE[^>]*>/,'')
  .replace(/\bid="([^"]+)"/g,(a,b)=>'id="'+p+b+'"').replace(/url\(#([^)]+)\)/g,(a,b)=>'url(#'+p+b+')')
  .replace(/href="#([^"]+)"/g,(a,b)=>'href="#'+p+b+'"');
 const s=new DOMParser().parseFromString(txt,'image/svg+xml').documentElement;
 for(const n of [...s.getElementsByTagName('sodipodi:namedview')])n.remove();
 for(const g of [...s.children])if(g.tagName==='g'&&lab(g)&&!keep.includes(lab(g)))g.remove();   // module drill marks (XXX) always go
 s.setAttribute('x',x);s.setAttribute('y',y);s.setAttribute('width',m.w*D);s.setAttribute('height',m.h*D);return s}
function target(){const v=$('pw').value;return v==='fit'?null:v==='custom'?(+$('cw').value||17):+v}
function layout(){const used=sel.reduce((a,i)=>a+M[i].w,0),T=target(),W=Math.max(T||used,used,0.5),H=7;
 let x=$('al').value==='center'&&T&&used<T?(T-used)/2:0;const pos=[];for(const i of sel){pos.push([i,x]);x+=M[i].w}return{used,T,W,H,pos}}
function holes(L){const out=[],miss=[],Hmm=L.H*MMI,Wmm=L.W*MMI;
 for(const[i,x]of L.pos){const m=M[i],h=m.k&&HD.modules[m.k];if(!h){miss.push(m.n);continue}
  const ox=x*MMI,oy=(L.H-m.h)/2*MMI;
  for(const o of h.holes){if(o[0]==='mount'&&$('mt').value==='corners')continue;
   const r=o.slice();r[1]=+(ox+o[1]).toFixed(3);r[2]=+(oy+o[2]).toFixed(3);out.push(r)}}
 if($('mt').value==='corners')for(const[x,y]of[[6.35,3.175],[6.35,Hmm-3.175],[Wmm-6.35,3.175],[Wmm-6.35,Hmm-3.175]])out.push(['mount',+x.toFixed(3),+y.toFixed(3)]);
 return{list:out,miss}}
function el(n,a,p){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e}
async function svg(mode){const L=layout(),o=el('svg',{xmlns:NS,'xmlns:xlink':'http://www.w3.org/1999/xlink','xmlns:inkscape':INK,
  width:L.W+'in',height:L.H+'in',viewBox:'0 0 '+L.W*D+' '+L.H*D});
 if(mode==='art'&&$('bg').value!=='none')el('rect',{width:'100%',height:'100%',fill:$('bg').value},o);
 const keep=mode==='fpe'?['Linework']:['Background','Linework','Jacks/Knobs'];
 for(const[i,x]of L.pos){const m=M[i],t=await get(m);o.appendChild(document.importNode(nest(t,x*D,(L.H-m.h)/2*D,m,keep),true))}
 if(mode==='art'){
  if($('fr').checked)el('rect',{x:.5,y:.5,width:L.W*D-1,height:L.H*D-1,fill:'none',stroke:'#000','stroke-width':1},o);
  const g=el('g',{id:'layer-XXX'},o);g.setAttributeNS(INK,'inkscape:groupmode','layer');g.setAttributeNS(INK,'inkscape:label','XXX');
  const k=D/MMI,col=$('bg').value==='#000000'?'#fff':'#000';
  for(const h of holes(L).list){const X=h[1]*k,Y=(L.H*MMI-h[2])*k,a=(h[0]==='mount'?3:2)*k;
   el('path',{d:'M'+(X-a)+' '+Y+'H'+(X+a)+'M'+X+' '+(Y-a)+'V'+(Y+a),stroke:col,'stroke-width':.6,fill:'none'},g);
   if(h[0]==='mount')el('circle',{cx:X,cy:Y,r:1.6*k,stroke:col,'stroke-width':.6,fill:'none'},g)}}
 return o}
async function draw(){
 $('sel').innerHTML='';sel.forEach((i,k)=>{const s=document.createElement('span');s.innerHTML=M[i].n+
  ' <button title="Move left">&#8249;</button><button title="Move right">&#8250;</button><button title="Remove">&times;</button>';
  const b=s.querySelectorAll('button');b[0].onclick=()=>{if(k){[sel[k-1],sel[k]]=[sel[k],sel[k-1]];draw()}};
  b[1].onclick=()=>{if(k<sel.length-1){[sel[k+1],sel[k]]=[sel[k],sel[k+1]];draw()}};b[2].onclick=()=>{sel.splice(k,1);draw()};$('sel').appendChild(s)});
 const L=layout(),{used,T}=L;
 $('meter').innerHTML=sel.length?('Modules: <b>'+used.toFixed(2)+'"</b>'+(T?(' of '+T+'" &middot; '+(used>T?'<b class="bad">'+(used-T).toFixed(2)+'" too wide</b>':((T-used).toFixed(2)+'" left'))):'')+' &middot; '+sel.length+' module'+(sel.length>1?'s':'')):'';
 const btn=['dl','dp','dd','df'];
 if(!sel.length){$('bp').innerHTML='';$('stage').innerHTML='<div class="empty">Click modules on the left to add them to the panel.</div>';btn.forEach(b=>$(b).disabled=true);$('warn').textContent='';return}
 const o=await svg('art');$('stage').innerHTML='';$('stage').appendChild(o);btn.forEach(b=>$(b).disabled=false);
 const H=holes(L);$('warn').innerHTML=H.miss.length?'No drill data yet for: <b>'+[...new Set(H.miss)].join(', ')+'</b>. Their holes are missing from the drill template and the Front Panel Express file.':'';
 $('hc').textContent=H.list.length+' holes';
 const bs=[...new Set(sel.map(i=>M[i].b).filter(Boolean))];
 $('bp').innerHTML=bs.length?'<p class="meter"><b>Build these modules:</b> '+bs.map(b=>'<a href="Modules/'+b+'.html">'+(M.find(m=>m.b===b).n)+'</a> (<a href="Modules/BOM/'+b+'.csv">BOM</a>)').join(' &middot; ')+'</p>':'';
 history.replaceState(null,'','#w='+$('pw').value+'&m='+sel.map(i=>M[i].n).join(','))}
const ser=o=>'<?xml version="1.0" encoding="UTF-8"?>\n'+new XMLSerializer().serializeToString(o);
function save(blob,name){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000)}
function nm(){return($('nm').value.trim()||'Serge_panel').replace(/[^\w.-]+/g,'_')}
function png(o,dpi,cb){const L=layout();let w=Math.round(L.W*dpi),h=Math.round(L.H*dpi);const sc=Math.min(1,16000/w);w=Math.round(w*sc);h=Math.round(h*sc);
 const img=new Image();img.onload=()=>{const c=document.createElement('canvas');c.width=w;c.height=h;c.getContext('2d').drawImage(img,0,0,w,h);c.toBlob(cb,'image/png')};
 img.src=URL.createObjectURL(new Blob([ser(o)],{type:'image/svg+xml'}))}
// ---- PDF drill template, 1:1 (one sheet, or tiled on Letter / A4 with overlap and alignment marks)
function pdf(){const L=layout(),H=holes(L),Wmm=L.W*MMI,Hmm=L.H*MMI,paper=$('pp').value,one=paper==='one',mg=one?12:4,pt=v=>(v*72/MMI).toFixed(2),dia=HD.diameters_mm;
 const PW=Wmm+2*mg,PH=Hmm+2*mg+(one?14:0);let c='0.4 w 0 0 0 RG\n'+pt(mg)+' '+pt(mg)+' '+pt(Wmm)+' '+pt(Hmm)+' re S\n';
 const circ=(x,y,r)=>{const k=0.5523*r;return pt(x+r)+' '+pt(y)+' m '+[[x+r,y+k,x+k,y+r,x,y+r],[x-k,y+r,x-r,y+k,x-r,y],[x-r,y-k,x-k,y-r,x,y-r],[x+k,y-r,x+r,y-k,x+r,y]].map(a=>a.map(pt).join(' ')+' c').join(' ')+' S\n'};
 for(const h of H.list){const x=mg+h[1],y=mg+h[2];
  if(h[0]==='slot'){c+=pt(x-h[3]/2)+' '+pt(y-h[4]/2)+' '+pt(h[3])+' '+pt(h[4])+' re S\n';continue}
  const r=(dia[h[0]]||4)/2;c+=circ(x,y,r)+pt(x-r-1.5)+' '+pt(y)+' m '+pt(x+r+1.5)+' '+pt(y)+' l '+pt(x)+' '+pt(y-r-1.5)+' m '+pt(x)+' '+pt(y+r+1.5)+' l S\n'}
 const esc=t=>t.replace(/[\\()]/g,'\\$&').replace(/[^\x20-\x7e]/g,'');
 const txt=(x,y,sz,t)=>'BT /F1 '+sz+' Tf '+pt(x)+' '+pt(y)+' Td ('+esc(t)+') Tj ET\n';
 const title=nm().replace(/_/g,' ')+' - drill template, '+L.W.toFixed(2)+' x 7 in, '+H.list.length+' holes',note='Print at 100% / actual size; the bar must measure 50 mm.'+(H.miss.length?' Missing: '+[...new Set(H.miss)].join(', '):'');
 const ty=mg+Hmm+5;if(one){c+=txt(mg,ty+4,9,nm().replace(/_/g,' ')+' - drill template, '+L.W.toFixed(2)+' x 7 in, '+H.list.length+' holes');
 c+=txt(mg,ty,7,'Print at 100% / actual size. The bar on the right must measure 50 mm. Hole circles are drawn at drill size.'+(H.miss.length?' Missing: '+[...new Set(H.miss)].join(', '):''));
 c+='1 w '+pt(mg+Wmm-50)+' '+pt(ty+1)+' m '+pt(mg+Wmm)+' '+pt(ty+1)+' l S\n'}
 const pages=[];
 if(paper==='one')pages.push({w:PW,h:PH,s:c});
 else{const[sw,sh]=paper==='a4'?[297,210]:[279.4,215.9],m=7,ov=15,uw=sw-2*m,uh=sh-2*m-10,
  nx=Math.max(1,Math.ceil((PW-ov)/(uw-ov))),ny=Math.max(1,Math.ceil((PH-ov)/(uh-ov)));
  for(let j=ny-1;j>=0;j--)for(let i=0;i<nx;i++){const ox=i*(uw-ov),oy=j*(uh-ov),n=pages.length+1,row=ny-j;
   let s='q '+pt(m)+' '+pt(m)+' '+pt(uw)+' '+pt(uh)+' re W n 1 0 0 1 '+pt(m-ox)+' '+pt(m-oy)+' cm\n'+c+'Q\n';
   s+='0.3 w 0.6 0.6 0.6 RG [2 2] 0 d '+pt(m)+' '+pt(m)+' '+pt(uw)+' '+pt(uh)+' re S [] 0 d 0 0 0 RG\n';
   if(i>0)s+='0.6 0 0.6 RG '+pt(m+ov)+' '+pt(m)+' m '+pt(m+ov)+' '+pt(m+uh)+' l S 0 0 0 RG\n';
   if(j<ny-1)s+='0.6 0 0.6 RG '+pt(m)+' '+pt(m+uh-ov)+' m '+pt(m+uw)+' '+pt(m+uh-ov)+' l S 0 0 0 RG\n';
   s+=txt(m,sh-m-4,8,title+'   Sheet '+n+' of '+nx*ny+(ny>1?' (row '+row+', column '+(i+1)+')':''));
   s+=txt(m,sh-m-9,7,note+(i>0?' Trim the left edge on the purple line and lay it over the previous sheet so the holes line up.':''));
   s+='1 w '+pt(sw-m-50)+' '+pt(sh-m-6)+' m '+pt(sw-m)+' '+pt(sh-m-6)+' l S\n';
   pages.push({w:sw,h:sh,s})}}
 const np=pages.length,objs=['<< /Type /Catalog /Pages 2 0 R >>','<< /Type /Pages /Kids ['+pages.map((_,k)=>(4+2*k)+' 0 R').join(' ')+'] /Count '+np+' >>',
  '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>'];
 pages.forEach((p,k)=>{objs.push('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 '+pt(p.w)+' '+pt(p.h)+'] /Resources << /Font << /F1 3 0 R >> >> /Contents '+(5+2*k)+' 0 R >>');
  objs.push('<< /Length '+p.s.length+' >>\nstream\n'+p.s+'endstream')});
 let s='%PDF-1.4\n';const off=[];objs.forEach((o,i)=>{off.push(s.length);s+=(i+1)+' 0 obj\n'+o+'\nendobj\n'});
 const x=s.length;s+='xref\n0 '+(objs.length+1)+'\n0000000000 65535 f \n'+off.map(o=>String(o).padStart(10,'0')+' 00000 n \n').join('')+'trailer\n<< /Size '+(objs.length+1)+' /Root 1 0 R >>\nstartxref\n'+x+'\n%%EOF';
 return new Blob([s],{type:'application/pdf'})}
// ---- zip (stored)
const CRC=(()=>{const t=[];for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0}return t})();
function crc(b){let c=~0;for(let i=0;i<b.length;i++)c=CRC[(c^b[i])&255]^(c>>>8);return(~c)>>>0}
function zip(files){const te=new TextEncoder(),parts=[],cen=[];let off=0;
 for(const f of files){const n=te.encode(f.name),d=f.data,c=crc(d),lh=new DataView(new ArrayBuffer(30));
  [[0,0x04034b50,4],[4,20,2],[6,0,2],[8,0,2],[10,0,2],[12,0x21,2],[14,c,4],[18,d.length,4],[22,d.length,4],[26,n.length,2],[28,0,2]].forEach(([o,v,s])=>s==4?lh.setUint32(o,v,true):lh.setUint16(o,v,true));
  parts.push(new Uint8Array(lh.buffer),n,d);const ch=new DataView(new ArrayBuffer(46));
  [[0,0x02014b50,4],[4,0x031e,2],[6,20,2],[8,0,2],[10,0,2],[12,0,2],[14,0x21,2],[16,c,4],[20,d.length,4],[24,d.length,4],[28,n.length,2],[30,0,2],[32,0,2],[34,0,2],[36,0,2],[38,((f.exec?0o100755:0o100644)<<16)>>>0,4],[42,off,4]].forEach(([o,v,s])=>s==4?ch.setUint32(o,v,true):ch.setUint16(o,v,true));
  cen.push(new Uint8Array(ch.buffer),n);off+=30+n.length+d.length}
 const cs=cen.reduce((a,b)=>a+b.length,0),e=new DataView(new ArrayBuffer(22));
 [[0,0x06054b50,4],[8,files.length,2],[10,files.length,2],[12,cs,4],[16,off,4]].forEach(([o,v,s])=>s==4?e.setUint32(o,v,true):e.setUint16(o,v,true));
 return new Blob([...parts,...cen,new Uint8Array(e.buffer)],{type:'application/zip'})}
async function fpdKit(){const L=layout(),H=holes(L),n=nm(),te=new TextEncoder(),kit='tools/fpd/';
 $('df').textContent='Preparing...';
 const fpe=await new Promise(async r=>png(await svg('fpe'),400,r));
 const job={diameters_mm:HD.diameters_mm,thickness_mm:2.0,panels:[{name:n,folder:'.',width_mm:+(L.W*MMI).toFixed(3),height_mm:+(L.H*MMI).toFixed(3),print_png:n+'_FPE.png',holes:H.list}]};
 const f=[{name:n+'/'+n+'.json',data:te.encode(JSON.stringify(job,null,1))},{name:n+'/'+n+'_FPE.png',data:new Uint8Array(await fpe.arrayBuffer())}];
 for(const s of['fpd_build.py','fpd_client.py']){const r=await fetch(kit+s);f.push({name:n+'/'+s,data:new Uint8Array(await r.arrayBuffer())})}
 f.push({name:n+'/Build panel (Mac).command',exec:1,data:te.encode('#!/bin/bash\n# Open Front Panel Designer first, then double-click this file.\ncd "$(dirname "$0")"\n/usr/bin/python3 fpd_build.py "'+n+'.json"\necho; read -n 1 -s -r -p "Press any key to close."\n')});
 f.push({name:n+'/Build panel (Windows).bat',data:te.encode('@echo off\r\nrem Open Front Panel Designer first, then double-click this file.\r\ncd /d "%~dp0"\r\npy fpd_build.py "'+n+'.json" || python fpd_build.py "'+n+'.json"\r\npause\r\n')});
 f.push({name:n+'/README.txt',data:te.encode(['Front Panel Express kit for '+n.replace(/_/g,' ')+', made with the Serge DIY Panel builder.','',
  'What is here','  '+n+'.json       panel size and every drill hole (mm, from the lower-left corner)','  '+n+'_FPE.png    the print artwork (linework only), placed over the whole plate',
  '  fpd_build.py, fpd_client.py   the script that drives Front Panel Designer','',
  'How to make the .fpd file','  1. Install Front Panel Designer (frontpanelexpress.com) and open it. Its built-in MCP server must be on (port 5757).',
  '  2. Mac: double-click "Build panel (Mac).command" (the first time, right-click > Open).','     Windows: double-click "Build panel (Windows).bat". Needs Python 3 (python.org).',
  '     Or in a terminal, in this folder:  python3 fpd_build.py "'+n+'.json"','  3. '+n+'.fpd is saved in this folder. Open it in Front Panel Designer, check it, and order.','',
  'Banana jacks get a double-D hole (8.33 mm across the round sides, 6.35 mm across the flats). Edit SETTINGS in fpd_build.py to change the material, colour or hole style.',
  H.miss.length?'\nNOTE: no drill data yet for '+[...new Set(H.miss)].join(', ')+'; add their holes by hand in Front Panel Designer.':'',
  'Check every hole against your own parts before ordering.'].join('\r\n'))});
 save(zip(f),n+'_FPE_kit.zip');$('df').textContent='Front Panel Express kit (.zip)'}
$('dl').onclick=async()=>save(new Blob([ser(await svg('art'))],{type:'image/svg+xml'}),nm()+'.svg');
$('dp').onclick=async()=>png(await svg('art'),150,b=>save(b,nm()+'.png'));
$('dd').onclick=()=>save(pdf(),nm()+'_drill_template.pdf');
$('df').onclick=()=>fpdKit().catch(e=>{$('df').textContent='Front Panel Express kit (.zip)';alert('Could not build the kit: '+e)});
$('cp').onclick=()=>{navigator.clipboard&&navigator.clipboard.writeText(location.href);$('cp').textContent='Link copied'};
['q','era'].forEach(i=>$(i).addEventListener('input',lib));['pw','cw','bg','al','fr','mt'].forEach(i=>$(i).addEventListener('change',()=>{$('cw').style.display=$('pw').value==='custom'?'':'none';draw()}));
const h=new URLSearchParams(location.hash.slice(1));
if(h.get('m'))sel=h.get('m').split(',').map(n=>M.findIndex(m=>m.s===n||m.n===n)).filter(i=>i>=0);
if(h.get('w'))$('pw').value=h.get('w');
lib();draw();
