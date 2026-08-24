const CACHE='xusheng-v26';
const ASSETS=['./','./index.html','./styles.css','./refinements.css','./app.js','./manifest.webmanifest','./icons/icon.svg','./assets/live2d/body_master_aligned.png','./assets/live2d/profile_character_integrated_v2.png','./assets/live2d/neck_body_clean_v2.png','./assets/live2d/cranium_earless_aligned.png','./assets/live2d/cranium_earless_refined_v2.png','./assets/live2d/cranium_halfblink_refined_v1.png','./assets/live2d/cranium_closed_refined_v1.png','./assets/live2d/wolf_ear_left_aligned.png','./assets/live2d/wolf_ear_right_aligned.png','./assets/live2d/eyes_halfblink_patch.png','./assets/live2d/eyes_closed_patch.png','./assets/live2d/collar_foreground_aligned.png'];

self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
 if(url.pathname.startsWith('/api/'))return;
 if(event.request.method!=='GET')return;
 const url=new URL(event.request.url);
 const isAppShell=event.request.mode==='navigate'||['.html','.css','.js'].some(extension=>url.pathname.endsWith(extension));
 if(isAppShell){
  event.respondWith(fetch(event.request,{cache:'no-store'}).then(response=>{const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(event.request,copy));return response}).catch(()=>caches.match(event.request).then(cached=>cached||caches.match('./index.html'))));
  return;
 }
 event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request).then(response=>{const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(event.request,copy));return response})));
});
