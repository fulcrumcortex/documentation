// Usage: node scripts/capture-screenshots.cjs /path/to/fulcrum-mail http://127.0.0.1:3187
// Requires a running local build and @playwright/test in that source checkout.
const {resolve,join}=require('node:path');
const {createRequire}=require('node:module');
const appRoot=resolve(process.argv[2]||'.');
const base=process.argv[3]||'http://127.0.0.1:3187';
if(!['127.0.0.1','localhost'].includes(new URL(base).hostname))throw new Error('Capture must use a local demonstration build');
const {chromium}=createRequire(join(appRoot,'package.json'))('@playwright/test');
const fs=require('node:fs');
const out=resolve(__dirname,'../assets/screenshots');fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await chromium.launch({channel:'chrome'});const ctx=await browser.newContext({viewport:{width:1440,height:960},serviceWorkers:'block',colorScheme:'light',timezoneId:'Australia/Sydney'});const page=await ctx.newPage();
await page.route('**/*',async route=>{const u=new URL(route.request().url());if(!['127.0.0.1','localhost'].includes(u.hostname))return route.abort();if(!u.pathname.startsWith('/api/'))return route.continue();let data=[];
if(u.pathname.endsWith('/auth/session'))data={user:{id:'guide-user',name:'Demo User',email:'demo@example.test',emailVerified:true},workspace:{id:'guide-workspace',name:'Demo workspace',kind:'personal',role:'owner',plan:'free',mailboxAddress:'demo@example.test',receivingReady:true,sendingReady:true,storageLimit:5000000000},workspaces:[{id:'guide-workspace',name:'Demo workspace',role:'owner'}],verificationRequired:false,onboardingRequired:false};
else if(u.pathname.endsWith('/mail/events'))return route.fulfill({contentType:'text/event-stream',body:'event: ready\ndata: {}\n\n'});
else if(u.pathname.endsWith('/mail/messages'))data=[{id:'demo-message',from:'Demo Team <team@example.test>',to:['demo@example.test'],subject:'Welcome to your demonstration workspace',text:'This inbox contains fictional data for the Fulcrum user guides.',snippet:'This inbox contains fictional data for the Fulcrum user guides.',receivedAt:'2026-11-05T01:00:00Z',folder:'inbox',unread:true,starred:false,labels:[]}];
else if(u.pathname.endsWith('/calendar/booking-pages'))data={pages:[],defaults:{timezone:'Australia/Sydney',duration:30,interval:15,bufferBefore:0,bufferAfter:0,noticeMinutes:120,horizonDays:60,weekly:[[],[{start:'09:00',end:'17:00'}],[{start:'09:00',end:'17:00'}],[{start:'09:00',end:'17:00'}],[{start:'09:00',end:'17:00'}],[{start:'09:00',end:'17:00'}],[]],overrides:[],conflicts:[{connectionId:null,calendarId:'demo-calendar'}],destination:{connectionId:null,calendarId:'demo-calendar'},meeting:'fulcrum',location:'',reminderMinutes:15}};
else if(u.pathname.endsWith('/calendar/connections'))data={connections:[],providers:[]};
else if(u.pathname.endsWith('/calendar/calendars'))data=[{id:'demo-calendar',name:'My calendar',isPrimary:true,color:'#00715b',timezone:'Australia/Sydney'}];
else if(u.pathname.endsWith('/calendar/events'))data={calendar:{id:'demo-calendar',name:'My calendar',color:'#00715b',timezone:'Australia/Sydney',isPrimary:true},events:[]};
else if(u.pathname.endsWith('/drive/docs-root'))data={id:'demo-docs-root',name:'Docs',isFolder:true};
else if(u.pathname.endsWith('/drive/usage'))data={used:12000,limit:5000000000};
else if(u.pathname.endsWith('/drive/files'))data=u.searchParams.has('parentId')?[]:[{id:'demo-folder',name:'Project resources',isFolder:true,mimeType:'inode/directory',size:0,updatedAt:'2026-11-05T00:00:00Z',createdAt:'2026-11-05T00:00:00Z',canEdit:true,canShare:true,ownerId:'guide-user'}];
else if(u.pathname.endsWith('/account/profile'))data={name:'Demo User',showJobTitle:false,showPhone:false};
else if(u.pathname.endsWith('/health'))data={status:'ok',revision:JSON.parse(fs.readFileSync(join(appRoot,'apps/web/lib/generated-release.json'))).sourceSha};
await route.fulfill({json:{data}});
});
for(const [path,file,ready] of [['mail','mail-inbox.png','text=Welcome to your demonstration workspace'],['calendar','calendar.png','h1'],['drive','drive.png','text=Project resources'],['docs','docs-home.png','text=Start a document']]){await page.goto(base+'/'+path);await page.locator(ready).first().waitFor();await page.waitForTimeout(1000);console.log(file,(await page.locator('body').innerText()).slice(0,170));await page.screenshot({path:out+'/'+file});if(path==='calendar'){const create=page.getByRole('button',{name:/Create event|New event/}).first();if(await create.count()){await create.click();await page.waitForTimeout(300);await page.screenshot({path:out+'/calendar-event.png'});}}}
await page.goto(base+'/calendar?tab=bookings');await page.getByRole('button',{name:'Create booking page',exact:true}).click();await page.getByLabel('Meeting name').waitFor();await page.screenshot({path:out+'/booking-editor.png'});
await browser.close();})();
