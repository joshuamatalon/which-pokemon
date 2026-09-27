// Self-check of data/questions.json against contract Q2/Q5/A6 rules, run by the stream builder
// before trusting the file. Not the official check (enabling owns test/check.py); this is a
// pre-flight so the stream doesn't hand off broken data.
import fs from "node:fs";

const q = JSON.parse(fs.readFileSync("data/questions.json", "utf8"));
const items = q.items;
let errors = [];

function words(s) { return s.trim().split(/\s+/).filter(Boolean); }

function syllables(word) {
  let w = word.toLowerCase().replace(/[^a-zé]/g, "");
  if (w.length <= 3) return 1;
  if (w.endsWith("e") && !w.endsWith("le")) w = w.slice(0, -1);
  const matches = w.match(/[aeiouy]+/g);
  return matches ? Math.max(1, matches.length) : 1;
}

const NEGATION_RE = /\b(not|no|never|none|nobody|nothing|nowhere|neither|nor|without)\b|n't\b/i;
const D8_WORDS = "sick doctor hospital medicine weight diet body fat thin money cost price buy pay rich poor allowance spend church god pray religion vote election date dating crush boyfriend girlfriend kiss fight argue argument divorce punish grounded die died death funeral grade grades test homework school class teacher work job office boss retire scared afraid sad cry lonely worry worried".split(" ");
const D8_RE = new RegExp("\\b(" + D8_WORDS.join("|") + ")\\b", "i");

if (items.length !== 15) errors.push(`item count ${items.length} != 15`);
const expectCycle = ["O","C","E","A","S","O","C","E","A","S","O","C","E","A","S"];
items.forEach((it, i) => {
  if (it.id !== `q${String(i+1).padStart(2,"0")}`) errors.push(`item ${i} id ${it.id} wrong`);
  if (it.trait !== expectCycle[i]) errors.push(`item ${it.id} trait ${it.trait} expected ${expectCycle[i]}`);
  const levels = it.answers.map(a=>a.level).sort((a,b)=>a-b);
  if (JSON.stringify(levels) !== JSON.stringify([-3,-1,1,3])) errors.push(`item ${it.id} levels ${levels} wrong`);

  const stemWords = words(it.stem);
  if (stemWords.length > 16) errors.push(`item ${it.id} stem ${stemWords.length} words > 16`);
  if (NEGATION_RE.test(it.stem)) errors.push(`item ${it.id} stem has negation: "${it.stem}"`);
  if (D8_RE.test(it.stem)) errors.push(`item ${it.id} stem has D8 word: "${it.stem}"`);

  let answerLens = [];
  it.answers.forEach(a => {
    const aw = words(a.text);
    answerLens.push(aw.length);
    if (aw.length > 10) errors.push(`item ${it.id} answer "${a.text}" ${aw.length} words > 10`);
    if (NEGATION_RE.test(a.text)) errors.push(`item ${it.id} answer has negation: "${a.text}"`);
    if (D8_RE.test(a.text)) errors.push(`item ${it.id} answer has D8 word: "${a.text}"`);
    if (!/^I /.test(a.text)) errors.push(`item ${it.id} answer doesn't start with "I ": "${a.text}"`);
    const ew = words(a.echo);
    if (ew.length > 12) errors.push(`item ${it.id} echo ${ew.length} words > 12: "${a.echo}"`);
    if (!/^you/i.test(a.echo)) errors.push(`item ${it.id} echo doesn't start with "you": "${a.echo}"`);
    if (NEGATION_RE.test(a.echo)) errors.push(`item ${it.id} echo has negation: "${a.echo}"`);
  });
  const spread = Math.max(...answerLens) - Math.min(...answerLens);
  if (spread > 4) errors.push(`item ${it.id} answer length spread ${spread} > 4`);

  // Flesch-Kincaid
  const allWordsArr = [...stemWords, ...it.answers.flatMap(a=>words(a.text))];
  const totalWords = allWordsArr.length;
  const stemSentences = (it.stem.match(/[.!?]+/g) || []).length || 1;
  const totalSentences = stemSentences + it.answers.length;
  const totalSyllables = allWordsArr.reduce((sum,w)=>sum+syllables(w),0);
  const fk = 0.39*(totalWords/totalSentences) + 11.8*(totalSyllables/totalWords) - 15.59;
  it._fk = fk;
  if (fk > 4.0) errors.push(`item ${it.id} FK grade ${fk.toFixed(2)} > 4.0`);

  // long word rule: no word of 4+ syllables except Pokemon/pokemon names
  for (const w of allWordsArr) {
    const clean = w.toLowerCase().replace(/[^a-zé]/g,"");
    if (!clean) continue;
    if (clean === "pokémon" || clean === "pokemon") continue;
    const syl = syllables(w);
    if (syl >= 4) errors.push(`item ${it.id} word "${w}" has ${syl} syllables (>=4)`);
  }
});

// D5: level-3 position balance
const posCounts = [0,0,0,0];
let nonMonotone = 0;
items.forEach(it => {
  const lv = it.answers.map(a=>a.level);
  const idx3 = lv.indexOf(3);
  posCounts[idx3]++;
  let asc = true, desc = true;
  for (let i=1;i<lv.length;i++){
    if (lv[i] < lv[i-1]) asc = false;
    if (lv[i] > lv[i-1]) desc = false;
  }
  if (!asc && !desc) nonMonotone++;
});
posCounts.forEach((c,i)=>{ if (c<3) errors.push(`D5 position ${i} only has level-3 answer ${c} times (<3)`); });
if (nonMonotone < 10) errors.push(`D5 non-monotone items ${nonMonotone} < 10`);

// facet distinctness per trait
const byTrait = {};
items.forEach(it => { (byTrait[it.trait] ??= []).push(it.facet); });
for (const [t, facets] of Object.entries(byTrait)) {
  if (new Set(facets).size !== 3) errors.push(`trait ${t} facets not distinct: ${facets}`);
}

const flavourCount = items.filter(it=>it.flavour).length;
if (flavourCount > 4) errors.push(`flavour count ${flavourCount} > 4`);

console.log(`Checked ${items.length} items.`);
console.log("FK grades:", items.map(it=>`${it.id}:${it._fk.toFixed(2)}`).join(" "));
console.log("Position counts for level-3:", posCounts);
console.log("Non-monotone count:", nonMonotone);
if (errors.length) {
  console.log(`\n${errors.length} ERRORS:`);
  errors.forEach(e=>console.log(" - "+e));
  process.exit(1);
} else {
  console.log("\nAll checks passed.");
}
