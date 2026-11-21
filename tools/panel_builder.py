"""The Panel builder page: pick modules, get one panel SVG. Called from make_site.py."""
import glob
import json
import os
import re
from urllib.parse import quote

GROUPS = [("Modern/Vector Graphics/Module", "SMMS metal / STS"), ("Paperface/Vector Graphics/Module", "Paperface"),
          ("SMMS/Paper/Vector Graphics/Module", "SMMS paper"), ("CGS/Vector Graphics", "CGS")]


def manifest(root, thumb):
    out = []
    for folder, era in GROUPS:
        for f in sorted(glob.glob(os.path.join(root, folder, "*.svg"))):
            head = open(f).read(1500)
            w, h = re.search(r'width="([\d.]+)in"', head), re.search(r'height="([\d.]+)in"', head)
            if not (w and h) or float(h.group(1)) > 7.01 or float(w.group(1)) > 9:
                continue
            if era == "CGS" and float(h.group(1)) > 6.9:          # CGS full panels are 7" tall; modules are 6.89"
                continue
            rel = os.path.relpath(f, root)
            png = rel.replace("Vector Graphics", "Images")[:-4] + ".png"
            out.append({"n": os.path.basename(f)[:-4].replace("_", " "), "e": era, "s": quote(rel), "w": float(w.group(1)),
                        "h": float(h.group(1)), "t": quote(thumb(png)) if os.path.exists(os.path.join(root, png)) else ""})
    return out


CSS = """
.pb{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.5fr);gap:22px;align-items:start}
.lib{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;position:sticky;top:60px;max-height:calc(100vh - 80px);display:flex;flex-direction:column}
.lib .f{display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap}.lib input,.lib select,.opts select,.opts input{font:inherit;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:#fff}
.lib input{flex:1;min-width:140px}
.lst{overflow-y:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:8px;padding-right:4px}
.it{border:1px solid var(--line);border-radius:8px;padding:6px;cursor:pointer;background:#faf9f5;text-align:center;font-size:.72rem;line-height:1.25}
.it:hover{border-color:var(--ink)}.it img{height:110px;max-width:100%;display:block;margin:0 auto 4px;object-fit:contain}
.it small{color:var(--muted)}
.opts{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:10px}
.sel{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.sel span{background:#fff;border:1px solid var(--line);border-radius:99px;padding:3px 4px 3px 10px;font-size:.8rem;display:flex;gap:2px;align-items:center}
.sel button{border:0;background:none;cursor:pointer;font-size:.9rem;padding:0 4px;color:var(--muted)}.sel button:hover{color:var(--accent)}
.stage{background:#ddd9cf;border-radius:10px;padding:14px;overflow-x:auto;min-height:200px;display:flex;align-items:center;justify-content:center}
.stage svg{max-width:100%;height:auto;background:#fff;box-shadow:0 6px 18px rgba(0,0,0,.15)}
.meter{font-size:.9rem;margin:6px 0}.meter b.bad{color:var(--accent)}
.empty{color:var(--muted);text-align:center;padding:40px}
@media(max-width:760px){.pb{grid-template-columns:1fr}.lib{position:static;max-height:420px}}
"""

JS = r"""
const M=JSON.parse(document.getElementById('man').textContent),D=96,cache={};let sel=[],uid=0;
const $=id=>document.getElementById(id);
function lib(){const q=$('q').value.toLowerCase(),er=$('era').value;$('lst').innerHTML='';
 M.forEach((m,i)=>{if(er&&m.e!==er)return;if(q&&!m.n.toLowerCase().includes(q))return;
  const d=document.createElement('div');d.className='it';d.title='Add '+m.n;
  d.innerHTML=(m.t?'<img loading="lazy" src="'+m.t+'" alt="">':'')+m.n+'<br><small>'+m.e+' · '+(+m.w).toFixed(2)+'"</small>';
  d.onclick=()=>{sel.push(i);draw()};$('lst').appendChild(d)})}
async function get(m){if(!cache[m.s]){const r=await fetch(m.s);cache[m.s]=await r.text()}return cache[m.s]}
function nest(txt,x,y,m){const p='m'+(++uid)+'-';
 txt=txt.replace(/<\?xml[^>]*>/,'').replace(/<!DOCTYPE[^>]*>/,'')
  .replace(/\bid="([^"]+)"/g,(a,b)=>'id="'+p+b+'"').replace(/url\(#([^)]+)\)/g,(a,b)=>'url(#'+p+b+')')
  .replace(/href="#([^"]+)"/g,(a,b)=>'href="#'+p+b+'"');
 const doc=new DOMParser().parseFromString(txt,'image/svg+xml'),s=doc.documentElement;
 s.querySelectorAll('namedview').forEach(n=>n.remove());
 for(const n of [...s.getElementsByTagName('sodipodi:namedview')])n.remove();
 s.setAttribute('x',x);s.setAttribute('y',y);s.setAttribute('width',m.w*D);s.setAttribute('height',m.h*D);return s}
function target(){const v=$('pw').value;return v==='fit'?null:v==='custom'?(+$('cw').value||17):+v}
async function draw(){
 $('sel').innerHTML='';sel.forEach((i,k)=>{const s=document.createElement('span');s.innerHTML=M[i].n+
  ' <button title="Move left">&#8249;</button><button title="Move right">&#8250;</button><button title="Remove">&times;</button>';
  const b=s.querySelectorAll('button');b[0].onclick=()=>{if(k){[sel[k-1],sel[k]]=[sel[k],sel[k-1]];draw()}};
  b[1].onclick=()=>{if(k<sel.length-1){[sel[k+1],sel[k]]=[sel[k],sel[k+1]];draw()}};b[2].onclick=()=>{sel.splice(k,1);draw()};$('sel').appendChild(s)});
 const used=sel.reduce((a,i)=>a+M[i].w,0),T=target(),W=T||Math.max(used,1),H=7;
 $('meter').innerHTML=sel.length?('Modules: <b>'+used.toFixed(2)+'"</b>'+(T?(' of '+T+'" &middot; '+(used>T?'<b class="bad">'+(used-T).toFixed(2)+'" too wide</b>':((T-used).toFixed(2)+'" left'))):'')+' &middot; '+sel.length+' module'+(sel.length>1?'s':'')):'';
 if(!sel.length){$('stage').innerHTML='<div class="empty">Click modules on the left to add them to the panel.</div>';$('dl').disabled=$('dp').disabled=true;return}
 const NS='http://www.w3.org/2000/svg',o=document.createElementNS(NS,'svg');
 o.setAttribute('xmlns',NS);o.setAttribute('xmlns:xlink','http://www.w3.org/1999/xlink');
 o.setAttribute('width',Math.max(W,used)+'in');o.setAttribute('height',H+'in');o.setAttribute('viewBox','0 0 '+Math.max(W,used)*D+' '+H*D);
 const bg=document.createElementNS(NS,'rect');bg.setAttribute('width','100%');bg.setAttribute('height','100%');bg.setAttribute('fill',$('bg').value);o.appendChild(bg);
 let x=$('al').value==='center'&&T&&used<T?(T-used)*D/2:0;
 for(const i of sel){const m=M[i],t=await get(m);o.appendChild(document.importNode(nest(t,x,(H-m.h)*D/2,m),true));x+=m.w*D}
 if($('fr').checked){const r=document.createElementNS(NS,'rect');r.setAttribute('x',.5);r.setAttribute('y',.5);
  r.setAttribute('width',Math.max(W,used)*D-1);r.setAttribute('height',H*D-1);r.setAttribute('fill','none');r.setAttribute('stroke','#000');r.setAttribute('stroke-width','1');r.setAttribute('id','panel-outline');o.appendChild(r)}
 $('stage').innerHTML='';$('stage').appendChild(o);$('dl').disabled=$('dp').disabled=false;
 history.replaceState(null,'','#w='+$('pw').value+'&m='+sel.map(i=>M[i].n).join(','))}
function svgText(){return '<?xml version="1.0" encoding="UTF-8"?>\n'+new XMLSerializer().serializeToString($('stage').querySelector('svg'))}
function save(blob,name){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),4000)}
function nm(){return($('nm').value.trim()||'Serge_panel').replace(/[^\w.-]+/g,'_')}
$('dl').onclick=()=>save(new Blob([svgText()],{type:'image/svg+xml'}),nm()+'.svg');
$('dp').onclick=()=>{const s=$('stage').querySelector('svg'),w=parseFloat(s.getAttribute('width'))*150,h=7*150,img=new Image();
 img.onload=()=>{const c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.drawImage(img,0,0,w,h);c.toBlob(b=>save(b,nm()+'.png'))};
 img.src=URL.createObjectURL(new Blob([svgText()],{type:'image/svg+xml'}))};
$('cp').onclick=()=>{navigator.clipboard&&navigator.clipboard.writeText(location.href);$('cp').textContent='Link copied'};
['q','era'].forEach(i=>$(i).addEventListener('input',lib));['pw','cw','bg','al','fr'].forEach(i=>$(i).addEventListener('change',()=>{$('cw').style.display=$('pw').value==='custom'?'':'none';draw()}));
const h=new URLSearchParams(location.hash.slice(1));
if(h.get('m'))sel=h.get('m').split(',').map(n=>M.findIndex(m=>m.s===n||m.n===n)).filter(i=>i>=0);
if(h.get('w'))$('pw').value=h.get('w');
lib();draw();
"""


def body(root, thumb):
    man = manifest(root, thumb)
    eras = []
    for _, era in GROUPS:
        if any(m["e"] == era for m in man):
            eras.append(era)
    return ("<style>%s</style><h1>Panel builder</h1><p class=\"lead\">Pick modules and get one panel: a single SVG with every module "
            "side by side, ready to print, to send to a panel maker, or to open in Inkscape. Each module keeps its layers, including "
            "the drill marks.</p>"
            '<div class="pb"><div class="lib"><div class="f"><input id="q" type="search" placeholder="Find a module..." aria-label="Find a module">'
            '<select id="era"><option value="">All eras</option>%s</select></div><div class="lst" id="lst"></div></div>'
            '<div><div class="opts"><label>Panel width <select id="pw"><option value="fit">Fit to modules</option>'
            '<option value="17" selected>17" full panel</option><option value="8">8" M-Class</option><option value="4.25">4.25" quarter panel</option>'
            '<option value="custom">Custom...</option></select></label><input id="cw" type="number" step="0.25" min="1" value="12" style="display:none;width:80px" aria-label="Custom width in inches">'
            '<label>Align <select id="al"><option value="left">Left</option><option value="center">Centre</option></select></label>'
            '<label>Background <select id="bg"><option value="#ffffff">White</option><option value="#000000">Black</option><option value="none">None</option></select></label>'
            '<label><input id="fr" type="checkbox" checked> Outline</label></div>'
            '<div class="sel" id="sel"></div><div class="meter" id="meter"></div><div class="stage" id="stage"></div>'
            '<div class="opts" style="margin-top:12px"><input id="nm" placeholder="Panel name" value="My_Serge_panel" aria-label="File name">'
            '<button class="btn pri" id="dl">Download SVG</button><button class="btn" id="cp">Copy link</button><button class="btn" id="dp">Download PNG</button></div>'
            '<div class="note">Modules are 7" tall (Loudest Warning format, 175 mm). Check the result against your own jacks, pots and '
            'case before drilling; module widths come from each module\'s artwork. Mixing eras works, but the styles will differ.</div></div></div>'
            '<script type="application/json" id="man">%s</script><script>%s</script>') % (
        CSS, "".join('<option>%s</option>' % e for e in eras), json.dumps(man).replace("</", "<\\/"), JS)
