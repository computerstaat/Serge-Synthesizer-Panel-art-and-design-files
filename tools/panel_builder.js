const M=JSON.parse(document.getElementById('man').textContent),HD=JSON.parse(document.getElementById('holes').textContent),D=96,MMI=25.4,cache={};
const NS='http://www.w3.org/2000/svg',INK='http://www.inkscape.org/namespaces/inkscape';
const $=id=>document.getElementById(id);
let era='',rows=[[],[]],ar=0,uid=0;
const nr=()=>+$('rw').value, all=()=>rows.slice(0,nr()).flat();
function lib(){const q=$('q').value.toLowerCase(),pc=$('pcb').checked;$('lst').innerHTML='';let c=0;
 M.forEach((m,i)=>{if(era&&m.e!==era)return;if(pc&&!m.b)return;if(q&&!m.n.toLowerCase().includes(q))return;c++;
  const d=document.createElement('div');d.className='it';d.title='Add '+m.n;
  d.innerHTML=(m.t?'<img loading="lazy" src="'+m.t+'" alt="">':'')+m.n+'<br><small>'+m.e+' · '+(+m.w).toFixed(2)+'"'+(m.k?'':' · no drill data')+'</small>'+(m.b?'<br><small class="pb1">PCB</small>':'');
  d.onclick=()=>{rows[nr()>1?ar:0].push(i);draw()};$('lst').appendChild(d)});
 if(!c)$('lst').innerHTML='<p class="muted">No modules match.</p>'}
async function get(m){if(!cache[m.s]){const r=await fetch(m.s);cache[m.s]=await r.text()}return cache[m.s]}
const lab=g=>g.getAttribute('inkscape:label')||'';
function nest(txt,x,y,m,keep){const p='m'+(++uid)+'-';
 txt=txt.replace(/<\?xml[^>]*>/,'').replace(/<!DOCTYPE[^>]*>/,'')
  .replace(/\bid="([^"]+)"/g,(a,b)=>'id="'+p+b+'"').replace(/url\(#([^)]+)\)/g,(a,b)=>'url(#'+p+b+')')
  .replace(/href="#([^"]+)"/g,(a,b)=>'href="#'+p+b+'"');
 const s=new DOMParser().parseFromString(txt,'image/svg+xml').documentElement;
 for(const n of [...s.getElementsByTagName('sodipodi:namedview')])n.remove();
 for(const g of [...s.children])if(g.tagName==='g'&&lab(g)&&!keep.includes(lab(g)))g.remove();   /* module drill marks (XXX) always go */
 s.setAttribute('x',x);s.setAttribute('y',y);s.setAttribute('width',m.w*D);s.setAttribute('height',m.h*D);return s}
function target(){const v=$('pw').value;return v==='fit'?null:v==='custom'?(+$('cw').value||17):+v}
const MARGIN=0.544;   /* side margin of the 17" panels */
function layoutRow(list){   /* modules sit as on the M-Class and 17" panels: about 2.2 mm between module outlines */
 const G=HD.gap||0.088,pos=[];let x=0,prev=null;
 for(const i of list){const m=M[i],o=m.o||[0,m.w];if(prev)x=prev.x+prev.o[1]+G-o[0];pos.push([i,x]);prev={x,o}}
 const first=list.length?(M[list[0]].o||[0])[0]:0,lm=list.length?M[list[list.length-1]]:null,
  used=list.length?pos[pos.length-1][1]+(lm.o||[0,lm.w])[1]-first:0;
 return{pos,used,first}}
function layout(){const T=target(),rs=rows.slice(0,nr()).map(layoutRow),mu=Math.max(0,...rs.map(r=>r.used)),
  W=T||Math.max(mu+2*MARGIN,0.5),H=7;
 for(const r of rs){const sh=(W-r.used)/2-r.first;for(const p of r.pos)p[1]+=sh}   /* each row centred */
 return{T,W,H,rs,n:rs.length}}
function holes(L,r){const out=[],miss=[],Hmm=L.H*MMI,Wmm=L.W*MMI;
 for(const[i,x]of L.rs[r].pos){const m=M[i],h=m.k&&HD.modules[m.k];if(!h){miss.push(m.n);continue}
  const ox=x*MMI,oy=(L.H-m.h)/2*MMI;
  for(const o of h.holes){if(o[0]==='mount'&&$('mt').value==='corners')continue;
   const q=o.slice();q[1]=+(ox+o[1]).toFixed(3);q[2]=+(oy+o[2]).toFixed(3);out.push(q)}}
 if($('mt').value==='corners')for(const[x,y]of[[6.35,3.175],[6.35,Hmm-3.175],[Wmm-6.35,3.175],[Wmm-6.35,Hmm-3.175]])out.push(['mount',+x.toFixed(3),+y.toFixed(3)]);
 return{list:out,miss}}
function footer(){const v=$('ft').value;return v==='custom'?$('ftc').value.trim():v}
function el(n,a,p){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e}
async function svg(mode,only){const L=layout(),idx=only==null?[...Array(L.n).keys()]:[only],TH=L.H*idx.length,
  o=el('svg',{xmlns:NS,'xmlns:xlink':'http://www.w3.org/1999/xlink','xmlns:inkscape':INK,width:L.W+'in',height:TH+'in',viewBox:'0 0 '+L.W*D+' '+TH*D});
 const dark=$('bg').value==='#000000',ink=dark?'#fff':'#1d1d1b';
 if(mode==='art'&&$('bg').value!=='none')el('rect',{width:'100%',height:'100%',fill:$('bg').value},o);
 const keep=mode==='fpe'?['Linework']:['Linework','Jacks/Knobs'];   /* one background for the whole panel, no per-module sheet edges */
 for(const[k,r]of idx.entries()){const y0=k*L.H;
  for(const[i,x]of L.rs[r].pos){const m=M[i],t=await get(m);o.appendChild(document.importNode(nest(t,x*D,(y0+(L.H-m.h)/2)*D,m,keep),true))}
  const ft=footer();
  if(ft){const t=el('text',{x:L.W*D-52.1,y:y0*D+663.5,style:'font-size:24px;font-family:Futura,"Century Gothic",sans-serif;text-anchor:end;fill:'+ink+';letter-spacing:0.8px'},o);t.textContent=ft}
  if(mode==='art'){
   if($('fr').checked)el('rect',{x:.5,y:y0*D+.5,width:L.W*D-1,height:L.H*D-1,fill:'none',stroke:dark?'#888':'#000','stroke-width':1},o);
   const g=el('g',{id:'layer-XXX-'+(r+1)},o);g.setAttributeNS(INK,'inkscape:groupmode','layer');g.setAttributeNS(INK,'inkscape:label','XXX');
   const kk=D/MMI;
   for(const h of holes(L,r).list){const X=h[1]*kk,Y=y0*D+(L.H*MMI-h[2])*kk,a=(h[0]==='mount'?3:2)*kk;
    el('path',{d:'M'+(X-a)+' '+Y+'H'+(X+a)+'M'+X+' '+(Y-a)+'V'+(Y+a),stroke:dark?'#fff':'#000','stroke-width':.6,fill:'none'},g);
    if(h[0]==='mount')el('circle',{cx:X,cy:Y,r:1.6*kk,stroke:dark?'#fff':'#000','stroke-width':.6,fill:'none'},g)}}}
 return o}
function chip(i,r,k){const s=document.createElement('span'),two=nr()>1;s.innerHTML=M[i].n+
  ' <button title="Move left">&#8249;</button><button title="Move right">&#8250;</button>'+(two?'<button title="Move to the other row">&#8597;</button>':'')+'<button title="Remove">&times;</button>';
 const b=s.querySelectorAll('button'),L=rows[r];
 b[0].onclick=()=>{if(k){[L[k-1],L[k]]=[L[k],L[k-1]];draw()}};
 b[1].onclick=()=>{if(k<L.length-1){[L[k+1],L[k]]=[L[k],L[k+1]];draw()}};
 if(two)b[2].onclick=()=>{L.splice(k,1);rows[1-r].push(i);draw()};
 b[b.length-1].onclick=()=>{L.splice(k,1);draw()};return s}
async function draw(){const two=nr()>1;$('rowpick').style.display=two?'':'none';
 $('sel').innerHTML='';
 rows.slice(0,nr()).forEach((list,r)=>{const g=document.createElement('div');g.className='rowsel'+(two&&r===ar?' act':'');
  if(two){const h=document.createElement('b');h.textContent='Row '+(r+1)+(r===0?' (top)':' (bottom)');h.onclick=()=>{ar=r;draw()};g.appendChild(h)}
  list.forEach((i,k)=>g.appendChild(chip(i,r,k)));if(two&&!list.length){const e=document.createElement('small');e.className='muted';e.textContent=' empty';g.appendChild(e)}
  $('sel').appendChild(g)});
 const L=layout(),T=L.T,cnt=all().length,mx=Math.max(0,...L.rs.map(r=>r.used));
 $('meter').innerHTML=cnt?(L.rs.map((r,k)=>(two?'Row '+(k+1)+': ':'Modules: ')+'<b>'+r.used.toFixed(2)+'"</b>'+(T?(' of '+T+'" &middot; '+(r.used>T-2*MARGIN?'<b class="bad">'+(r.used-T+2*MARGIN).toFixed(2)+'" too wide (keep 0.54" each side)</b>':((T-2*MARGIN-r.used).toFixed(2)+'" left'))):'')).join('<br>')+' &middot; '+cnt+' module'+(cnt>1?'s':'')):'';
 const btn=['dl','dp','dd','df','bm'];
 if(!cnt){$('bp').innerHTML='';$('stage').innerHTML='<div class="empty">Click modules on the left to add them to the panel.</div>';btn.forEach(b=>$(b).disabled=true);$('warn').textContent='';$('hc').textContent='';return}
 const o=await svg('art');$('stage').innerHTML='';$('stage').appendChild(o);btn.forEach(b=>$(b).disabled=false);
 const Hs=L.rs.map((_,r)=>holes(L,r)),miss=[...new Set(Hs.flatMap(h=>h.miss))];
 $('warn').innerHTML=miss.length?'No drill data yet for: <b>'+miss.join(', ')+'</b>. Their holes are missing from the drill template and the Front Panel Express file.':'';
 $('hc').textContent=Hs.reduce((a,h)=>a+h.list.length,0)+' holes';
 const bs=[...new Set(all().map(i=>M[i].b).filter(Boolean))];
 $('bp').innerHTML=bs.length?'<p class="meter"><b>Build these modules:</b> '+bs.map(b=>'<a href="Modules/'+b+'.html">'+(M.find(m=>m.b===b).n)+'</a> (<a href="Modules/BOM/'+b+'.csv">BOM</a>)').join(' &middot; ')+'</p>':'';
 const enc=l=>l.map(i=>M[i].n).join(',');
 history.replaceState(null,'','#w='+$('pw').value+'&m='+enc(rows[0])+(two?'&r=2&m2='+enc(rows[1]):'')+($('ft').value?'&f='+encodeURIComponent(footer()):''))}
const ser=o=>'<?xml version="1.0" encoding="UTF-8"?>\n'+new XMLSerializer().serializeToString(o);
function save(blob,name){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000)}
function nm(){return($('nm').value.trim()||'Serge_panel').replace(/[^\w.-]+/g,'_')}
function png(o,dpi,cb){const w0=parseFloat(o.getAttribute('width')),h0=parseFloat(o.getAttribute('height'));let w=Math.round(w0*dpi),h=Math.round(h0*dpi);const sc=Math.min(1,16000/Math.max(w,h));w=Math.round(w*sc);h=Math.round(h*sc);
 const img=new Image();img.onload=()=>{const c=document.createElement('canvas');c.width=w;c.height=h;c.getContext('2d').drawImage(img,0,0,w,h);c.toBlob(cb,'image/png')};
 img.src=URL.createObjectURL(new Blob([ser(o)],{type:'image/svg+xml'}))}
// ---- PDF drill template, 1:1 (one sheet, or tiled on Letter / A4 with overlap and alignment marks); one set per row
function pdfPages(L,r,label){const H=holes(L,r),Wmm=L.W*MMI,Hmm=L.H*MMI,paper=$('pp').value,one=paper==='one',mg=one?12:4,pt=v=>(v*72/MMI).toFixed(2),dia=HD.diameters_mm;
 const PW=Wmm+2*mg,PH=Hmm+2*mg+(one?14:0);let c='0.4 w 0 0 0 RG\n'+pt(mg)+' '+pt(mg)+' '+pt(Wmm)+' '+pt(Hmm)+' re S\n';
 const circ=(x,y,r)=>{const k=0.5523*r;return pt(x+r)+' '+pt(y)+' m '+[[x+r,y+k,x+k,y+r,x,y+r],[x-k,y+r,x-r,y+k,x-r,y],[x-r,y-k,x-k,y-r,x,y-r],[x+k,y-r,x+r,y-k,x+r,y]].map(a=>a.map(pt).join(' ')+' c').join(' ')+' S\n'};
 for(const h of H.list){const x=mg+h[1],y=mg+h[2];
  if(h[0]==='slot'){c+=pt(x-h[3]/2)+' '+pt(y-h[4]/2)+' '+pt(h[3])+' '+pt(h[4])+' re S\n';continue}
  const r=(dia[h[0]]||4)/2;c+=circ(x,y,r)+pt(x-r-1.5)+' '+pt(y)+' m '+pt(x+r+1.5)+' '+pt(y)+' l '+pt(x)+' '+pt(y-r-1.5)+' m '+pt(x)+' '+pt(y+r+1.5)+' l S\n'}
 const esc=t=>t.replace(/[\\()]/g,'\\$&').replace(/[^\x20-\x7e]/g,'');
 const txt=(x,y,sz,t)=>'BT /F1 '+sz+' Tf '+pt(x)+' '+pt(y)+' Td ('+esc(t)+') Tj ET\n';
 const title=nm().replace(/_/g,' ')+label+' - drill template, '+L.W.toFixed(2)+' x 7 in, '+H.list.length+' holes',note='Print at 100% / actual size; the bar must measure 50 mm.'+(H.miss.length?' Missing: '+[...new Set(H.miss)].join(', '):'');
 const ty=mg+Hmm+5;if(one){c+=txt(mg,ty+4,9,nm().replace(/_/g,' ')+label+' - drill template, '+L.W.toFixed(2)+' x 7 in, '+H.list.length+' holes');
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
 return pages}
function pdf(){const L=layout(),pt=v=>(v*72/MMI).toFixed(2),pages=[];
 for(let r=0;r<L.n;r++)pages.push(...pdfPages(L,r,L.n>1?' - row '+(r+1):''));
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
async function fpdKit(){const L=layout(),n=nm(),te=new TextEncoder(),kit='tools/fpd/',panels=[],f=[];
 $('df').textContent='Preparing...';const miss=[];
 for(let r=0;r<L.n;r++){const pn=L.n>1?n+'_row'+(r+1):n,H=holes(L,r);miss.push(...H.miss);
  const fpe=await new Promise(async res=>png(await svg('fpe',r),400,res));
  panels.push({name:pn,folder:'.',width_mm:+(L.W*MMI).toFixed(3),height_mm:+(L.H*MMI).toFixed(3),print_png:pn+'_FPE.png',holes:H.list});
  f.push({name:n+'/'+pn+'_FPE.png',data:new Uint8Array(await fpe.arrayBuffer())})}
 f.unshift({name:n+'/'+n+'.json',data:te.encode(JSON.stringify({diameters_mm:HD.diameters_mm,thickness_mm:2.0,panels},null,1))});
 for(const s of['fpd_build.py','fpd_client.py']){const r=await fetch(kit+s);f.push({name:n+'/'+s,data:new Uint8Array(await r.arrayBuffer())})}
 f.push({name:n+'/Build panel (Mac).command',exec:1,data:te.encode('#!/bin/bash\n# Open Front Panel Designer first, then double-click this file.\ncd "$(dirname "$0")"\n/usr/bin/python3 fpd_build.py "'+n+'.json"\necho; read -n 1 -s -r -p "Press any key to close."\n')});
 f.push({name:n+'/Build panel (Windows).bat',data:te.encode('@echo off\r\nrem Open Front Panel Designer first, then double-click this file.\r\ncd /d "%~dp0"\r\npy fpd_build.py "'+n+'.json" || python fpd_build.py "'+n+'.json"\r\npause\r\n')});
 const um=[...new Set(miss)];
 f.push({name:n+'/README.txt',data:te.encode(['Front Panel Express kit for '+n.replace(/_/g,' ')+', made with Build a panel on the Serge DIY site.','',
  'What is here','  '+n+'.json       the size of '+(L.n>1?'each panel ('+L.n+' rows)':'the panel')+' and every drill hole (mm, from the lower-left corner)',
  '  *_FPE.png    the print artwork (linework only), placed over the whole plate',
  '  fpd_build.py, fpd_client.py   the script that drives Front Panel Designer','',
  'How to make the .fpd file'+(L.n>1?'s':''),'  1. Install Front Panel Designer (frontpanelexpress.com) and open it. Its built-in MCP server must be on (port 5757).',
  '  2. Mac: double-click "Build panel (Mac).command" (the first time, right-click > Open).','     Windows: double-click "Build panel (Windows).bat". Needs Python 3 (python.org).',
  '     Or in a terminal, in this folder:  python3 fpd_build.py "'+n+'.json"','  3. The .fpd '+(L.n>1?'files are':'file is')+' saved in this folder. Open in Front Panel Designer, check, and order.','',
  'Banana jacks get a double-D hole (8.33 mm across the round sides, 6.35 mm across the flats). Edit SETTINGS in fpd_build.py to change the material, colour or hole style.',
  um.length?'\nNOTE: no drill data yet for '+um.join(', ')+'; add their holes by hand in Front Panel Designer.':'',
  'Check every hole against your own parts before ordering.'].join('\r\n'))});
 save(zip(f),n+'_FPE_kit.zip');$('df').textContent='Front Panel Express kit (.zip)'}
// ---- one Mouser order for every chosen module (Ken Stone boards first; every sub-board of a module is included)
function csvParse(t){const rows=[];let row=[],f='',q=false;for(let i=0;i<t.length;i++){const c=t[i];
  if(q){if(c==='"'){if(t[i+1]==='"'){f+='"';i++}else q=false}else f+=c}
  else if(c==='"')q=true;else if(c===','){row.push(f);f=''}else if(c==='\n'||c==='\r'){if(c==='\r'&&t[i+1]==='\n')i++;row.push(f);f='';if(row.length>1||row[0])rows.push(row);row=[]}else f+=c}
 if(f||row.length){row.push(f);rows.push(row)}return rows}
const csvq=v=>/[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;
async function bom(){const cnt={};for(const i of all()){const b=M[i].b;if(b)cnt[b]=(cnt[b]||0)+1}
 const mouser={},other=[],used=[],none=[],te=new TextEncoder();
 for(const[slug,k]of Object.entries(cnt)){const fl=(HD.mouser||{})[slug]||[];if(!fl.length){none.push(slug);continue}
  const ken=fl.filter(b=>/^cgs/.test(b)),pick=ken.length?ken:[fl[0]];
  for(const b of pick){used.push(slug+' / '+b.toUpperCase().replace(/_/g,' ')+(k>1?' x'+k:''));
   const r=csvParse(await (await fetch('Modules/BOM/mouser/'+slug+'__'+b+'.csv')).text());
   for(const row of r.slice(1)){const key=row[0]||row[1];if(!key)continue;const q=(+row[3]||0)*k;
    if(mouser[key]){mouser[key][3]+=q;if(!mouser[key][5].includes(row[5]))mouser[key][5]+='; '+row[5]}else mouser[key]=[row[0],row[1],row[2],q,row[4],row[5]]}
   try{const o=csvParse(await (await fetch('Modules/BOM/mouser/'+slug+'__'+b+'_not_at_mouser.csv')).text());
    if(!other.length)other.push(['Module','Board','Copies'].concat(o[0]));for(const row of o.slice(1))other.push([slug,b,String(k)].concat(row))}catch(e){}}}
 const head='Mouser Part Number,Manufacturer Part Number,Manufacturer,Quantity,Description,Customer Part Number';
 const body=Object.values(mouser).map(r=>r.map(v=>csvq(String(v))).join(',')).join('\r\n');
 const n=nm(),f=[{name:n+'_Mouser_upload.csv',data:te.encode(head+'\r\n'+body+'\r\n')}];
 if(other.length)f.push({name:n+'_other_parts.csv',data:te.encode(other.map(r=>r.map(v=>csvq(String(v))).join(',')).join('\r\n')+'\r\n')});
 f.push({name:'README.txt',data:te.encode(['Parts for '+n.replace(/_/g,' ')+', made with Build a panel on the Serge DIY site.','',
  'Boards included (quantities multiplied by how many of each module are on the panel):',...used.map(u=>'  '+u),'',
  none.length?'No Mouser file yet for: '+none.join(', ')+' (see their build pages for BOMs).\r\n':'',
  n+'_Mouser_upload.csv: upload at mouser.com/bomtool. Lines marked UNVERIFIED have not been checked for stock and price.',
  n+'_other_parts.csv: jacks, knobs, PCBs and parts Mouser does not stock.','',
  'Panel hardware (jacks, pots, switches on the panel) is listed per module in each module\'s BOM spreadsheet on its build page.'].join('\r\n'))});
 save(zip(f),n+'_parts.zip')}
$('dl').onclick=async()=>save(new Blob([ser(await svg('art'))],{type:'image/svg+xml'}),nm()+'.svg');
$('dp').onclick=async()=>png(await svg('art'),150,b=>save(b,nm()+'.png'));
$('dd').onclick=()=>save(pdf(),nm()+'_drill_template.pdf');
$('df').onclick=()=>fpdKit().catch(e=>{$('df').textContent='Front Panel Express kit (.zip)';alert('Could not build the kit: '+e)});
$('bm').onclick=()=>bom().catch(e=>alert('Could not build the parts list: '+e));
$('cp').onclick=()=>{navigator.clipboard&&navigator.clipboard.writeText(location.href);$('cp').textContent='Link copied'};
$('q').addEventListener('input',lib);$('pcb').addEventListener('change',lib);
for(const b of document.querySelectorAll('#eras .chip'))b.onclick=()=>{for(const x of document.querySelectorAll('#eras .chip'))x.classList.remove('on');b.classList.add('on');era=b.dataset.v;lib()};
for(const b of document.querySelectorAll('#rowpick button'))b.onclick=()=>{ar=+b.dataset.r;draw()};
['pw','cw','bg','fr','mt','rw','ft','ftc'].forEach(i=>$(i).addEventListener('change',()=>{$('cw').style.display=$('pw').value==='custom'?'':'none';$('ftc').style.display=$('ft').value==='custom'?'':'none';if(nr()<2)ar=0;draw()}));
const h=new URLSearchParams(location.hash.slice(1)),dec=v=>v?v.split(',').map(n=>M.findIndex(m=>m.s===n||m.n===n)).filter(i=>i>=0):[];
rows[0]=dec(h.get('m'));rows[1]=dec(h.get('m2'));if(h.get('r')==='2')$('rw').value='2';
if(h.get('w'))$('pw').value=h.get('w');
if(h.get('f')){const f=h.get('f');if([...$('ft').options].some(o=>o.value===f))$('ft').value=f;else{$('ft').value='custom';$('ftc').value=f;$('ftc').style.display=''}}
lib();draw();
