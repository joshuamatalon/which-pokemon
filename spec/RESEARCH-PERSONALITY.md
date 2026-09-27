# Personality research behind the quiz

Subsystem research note, 2026-09-27. It answers the brief in PLAN.md and ruling 2. Every decision at the
end is inherited word for word by `spec/CONTRACT.md`. Sources are numbered in the list at the bottom; the
last column of that list says whether I read the paper or its full text this session, or cite it from
the record.

## 1. What personality is made of

The Big Five is the best-supported map of how people differ. It came out of the lexical approach: if a
difference between people matters, languages grow words for it, and factor analysis of those words keeps
finding the same five dimensions [1]. McCrae and Costa found the same five in translated instruments across
many cultures and argued the structure is a human universal [2]. The Life Outcomes of Personality
Replication project re-tested published links between the five traits and life outcomes with
preregistered samples, and most of them held [3]. The five are Openness, Conscientiousness, Extraversion,
Agreeableness and Negative Emotionality (Neuroticism).

HEXACO adds a sixth factor, Honesty-Humility, and splits emotional content differently [4]. It predicts
some moral outcomes better. I did not adopt it for this quiz. A family quiz with a positive-only result
cannot score honesty without implying that a low scorer is dishonest, and honesty items are the most
socially loaded kind [4, 20]. Honesty is also hard to read off a Pokémon's canon. The five shared factors
carry the rest of what HEXACO measures.

Traits are continuous. Most people sit near the middle of each one, and the dimensions do not split
people into kinds [2, 19]. The quiz therefore places people at points in a space and never sorts them
into types.

## 2. Brief instruments

Four short Big Five measures show what a quiz of 10 to 20 items can and cannot do.

| Instrument | Items | Per trait | Internal consistency (alpha) | Retest | Source |
|---|---|---|---|---|---|
| TIPI | 10 | 2 | .40 to .73 | mean .72 over 6 weeks | [5] |
| BFI-10 | 10 | 2 | not reported as alpha | .65 to .79 over 6 to 8 weeks | [6] |
| Mini-IPIP | 20 | 4 | about .60 or higher | close to the parent 50-item test | [7] |
| BFI-2-XS | 15 | 3 | mean .59 to .63, range .49 to .73 | mean .70 and .76 in two samples | [8] |

Short forms keep the broad meaning of each trait and lose precision. The BFI-2-XS scales correlate with
the full BFI-2 domains at about .90 [8]. The same paper reports that the extra-short form keeps about 80%
of the full scales' variance [8]. TIPI scales converge with the 44-item BFI at a mean of .77 [5]. The
BFI-10 keeps about 70% of the full BFI variance [6].

Brief scales show higher retest reliability than alpha, because their authors pick items that cover
different sides of a trait on purpose [5, 8]. A low alpha is the price of breadth, and retest reliability
is the better guide for a three-item scale.

Credé and colleagues showed the cost of going too short [9]. One-item and two-item measures understate how
much personality predicts, while slightly longer measures recover much of that loss. Three items per
trait is the shortest length with published retest figures near .70 [8].

## 3. How good items are written

The scale-construction literature agrees on a short list of rules [21, 13, 12].

- One idea per item. A double-barrelled item ("I am talkative and organised") cannot be answered by
  someone who is one and not the other.
- Balanced keying. When half the items run the other way, a habit of agreeing cancels out [10]. Balance
  is the textbook fix for acquiescence.
- Watch social desirability. People lean toward the answer that sounds better, more so when the topic is
  sensitive [20]. Options must be equally acceptable.
- Concrete beats abstract. Items about behaviour in a named situation are easier to answer than trait
  adjectives, and frame-of-reference research shows context can raise validity [16].
- Plain words for children. Short statements, simple words and familiar situations help young readers
  [13]. Borgers and Hox found readable questions and clear introductions raised children's reliability
  [12].

## 4. Children as respondents

Self-report gets better with age. Soto and colleagues studied Big Five self-reports from age 10 to 20 in
a large internet sample [10]. At the younger ages, children differed widely in acquiescence, which is the
habit of agreeing with statements regardless of content. That habit distorted the scales, and trait
coherence rose with age [10].

Negative wording fails with young children. Marsh gave self-concept items to children in grades 2 to 5
and found that second-graders often answered "true" to negatively worded items even when the rest of
their answers were positive [11]. Borgers and Hox reached the same verdict in a secondary analysis of
several child surveys: negatively formulated questions lowered reliability, and they advised avoiding them
[12].

Children also cope worse with many response options. Across their child data sets, more response options
lowered reliability, the opposite of the adult pattern, and offering a midpoint lowered alpha [12]. Fully
labelled options helped [12].

The youngest age with a validated Big Five self-report is about seven, and those scales show the lowest
reliabilities in a 2025 systematic review [13]. The review attributes the drop to few items per dimension
and to young readers' limits [13].

What this means for Milo, who is eight. He can take the quiz, if it is written for him: short concrete
questions, familiar everyday situations, no negation, no agree-or-disagree scale, few labelled options.
His answers will still be noisier than an adult's, and the result must not claim more precision than his
answers carry.

## 5. Forced choice or Likert (ruling 2a)

A Likert item asks how much you agree with a statement. It is quick and scores cleanly, but it invites
acquiescence, and acquiescence is largest in children [10]. Reversed Likert items, the usual fix, are the
very items young children misread [11, 12].

Classic forced choice shows two or more statements that measure different traits and asks which is more
like you. It resists faking in high-stakes selection [15]. Its scores are ipsative: choosing one trait
always costs another, so every taker's scores sum to the same total and cannot all be high or all be low
[14]. Brown and Maydeu-Olivares showed that ipsative scoring distorts profiles, scale correlations and
reliability, and that fixing it needs Thurstonian item response models fitted on large samples [14]. With
five traits and 15 items there is no sample to fit and no room to absorb the distortion. Faking resistance
also matters little in a family quiz, where no one gains by lying.

A third format fits this audience: one situation, several answers, each answer a concrete behaviour at a
different level of a single trait. It is how game-like personality measures work; the Game-like
Personality Measure uses choices whose options represent different levels of a factor, and its authors
report convergent validity with standard inventories and less faking and careless responding [17]. It
has no agree-or-disagree step, so acquiescence has nothing to act on. It needs no negated wording. It is
not ipsative, because every option of an item scores the same trait. And it reads like a quiz, which is
what the family expects.

The quiz therefore uses single-trait graded choice with four fully labelled behaviour options and no midpoint.

## 6. What validity is lost when validated items become scenario items (ruling 2b)

Rewording a validated item into a story item costs three things.

- The validity evidence stops transferring. TIPI, BFI-10 and Mini-IPIP figures belong to their exact
  wording [5, 6, 7]. A rewritten item is a new item with unknown loadings until it is tested on people.
- Situations add their own variance. A scenario answer reflects the trait and also how the person reads
  that situation. Contextualized items predict better within their context [16], but a Pokémon-world
  context is one nobody lives in, so answers may reflect fantasy preference more than habit.
- Content can drift. A writer who dresses up an item may slide from the trait into a neighbouring one,
  for example from sociability into enthusiasm for adventure (Openness).

The contract limits each loss.

- Every item names a public-domain IPIP source item and a BFI-2 facet, and its four options must be
  behaviours that express that source item's content at four levels.
- Stems describe real, everyday situations that an 8-year-old and a 70-year-old both know. At most four
  of the 15 stems may use Pokémon flavour, and those still ask about real behaviour. No item needs any
  Pokémon knowledge.
- Each trait's three items sample three different facets, which is how the BFI-2-XS protects breadth [8].
- The quiz never claims to be a validated instrument. The result text cannot say "science says you are"
  and must present the match as a reading of today's answers.

No study measures the validity of this exact quiz, and this project will not collect the data to do so.
The honest statement is that the items follow validated content and design rules, and the size of the
loss is unmeasured.

## 7. Retest reliability at 15 items for a child reader (ruling 2c)

Adults on the BFI-2-XS, which also has 15 items, show domain retest reliability of about .70 to .76 over
two to three months [8]. For children, the one short child questionnaire in the 2025 review had the
lowest reliabilities of any instrument reviewed [13]. A Spanish validation of the longer 65-item BFQ-C,
with children from 8 upward, reported retest from .62 to .84 [18]. A 15-item quiz for an 8-year-old will
sit below both. A trait-level retest near .6 is a fair planning figure, and it is an estimate, since no
published study reports this exact case.

The matching step makes this worse, and I measured by how much with a simulation. I built a synthetic
pool of 160 profiles spread through the trait space. I then simulated takers whose answers carry random
error, with the error set so that the trait retest correlation matched the adult or the child figure.

| Trait retest (simulated) | Same Pokémon on a retake | Retake lands in first answer's top 3 |
|---|---|---|
| .74 (adult, BFI-2-XS level) | about 14% | about 30% |
| .60 (child planning figure) | about 8% | about 18% |

These are model results, not measurements of real people. They say something plain: with 150 or more
outcomes, a 15-item quiz taken again weeks later will usually give a different Pokémon, for adults too.
The traits are fairly stable; the single nearest Pokémon is not, because neighbouring profiles sit close
together. Same-day retakes with the same answers give the same result, because scoring is deterministic.

The contract handles this in three ways. It shows the taker's five trait positions next to the Pokémon,
since that is the stable part. It bans any claim that the match is permanent or "true". And it writes
every item for the youngest reader, which removes the known child failure modes named in section 4.

## 8. Why the quiz does not sort people into types

The MBTI sorts people into 16 types by cutting four scales at their midpoints. Pittenger reviewed its
record and found poor retest agreement for type [19]. In the study he cites, McCarley and Carskadon found
that under half of takers kept all four letters over five weeks [19]. Cutting a continuous score at the
middle is the cause: most people sit near the cut, so small changes flip the letter. McCrae and Costa also
found the MBTI scales map onto four of the Big Five, with no evidence of the bimodal split that true types
would need [2].

The quiz avoids that design. Traits stay continuous from -1 to 1, the match is a nearest point in the
space, and no screen says "you are an introvert" or "you are type X". Sections 7 and 8 together are the
reason the result screen shows positions on bars with two named, positive poles.

## 9. The Barnum effect and how the result text avoids it

Forer gave 39 students one identical personality sketch built from astrology-book lines, and they rated
it as a close fit [22]. People accept vague, flattering descriptions as personal, and acceptance
rises when the text is favourable and when the reader believes it was written for them [23, 24]. A
positive-only Pokémon result is exactly the setting where Barnum text thrives.

The contract turns that into rules. Every sentence in a result must depend on something checkable: the
taker's own answers, which it quotes, or a species fact with a source. Stock Barnum lines are banned by
name. The result quotes two of the taker's own answers, so two takers who land on the same Pokémon still
read different text. No why-sentence may appear in two profiles. Each why-sentence must carry an anchor
word from that species' own Pokédex text, genus, name or media list.

## 10. Enjoyable, thought provoking, and not too personal

Tourangeau and Yan describe three ways a question becomes sensitive: it intrudes on private matters, it
risks disclosure to others, or it has a socially desirable answer [20]. A family quiz taken on a shared
phone at a table has all three risks. The safe ground is ordinary behaviour in ordinary situations:
planning a trip, a free afternoon, a board game, a new place, a surprise, a group project.

Items become enjoyable when every answer is a real, likeable choice, so the taker has to think about what
they would actually do. That is the same property that controls social desirability [15, 20]. A question
with one obviously good answer is dull and gives bad data. A question where all four answers sound like
people you like is fun, and it measures.

The quiz excludes health, the body, money, sex, religion, politics, family conflict, grief, school or work
performance, and fears or sadness. The Negative Emotionality items keep to its lighter sides, such as
waiting for news, a sudden change of plan, and being rushed. The quiz does not sample the Depression facet
of the BFI-2 at all.

## Decisions taken from the evidence

D1. The trait model is the Big Five, scored as five continuous dimensions from -1 to 1. Negative
Emotionality is reversed and named Steadiness, so both poles of every trait have a positive label.
HEXACO Honesty-Humility is not measured.

D2. The quiz has 15 items, three per trait, and each trait's three items sample three different BFI-2
facets.

D3. Every item is a single-trait graded choice: one everyday situation and four fully labelled behaviour
options at levels -3, -1, 1 and 3 of that one trait. No agree-or-disagree scale, no midpoint, no
multi-trait ipsative blocks.

D4. No item or option uses negation, and all four options of an item must be equally acceptable
behaviours.

D5. Keying balance comes from option order. The top-level option sits in each of the four display
positions at least three times across the 15 items, and at least ten items show their options in a
non-monotone order.

D6. Every item is written for an 8-year-old reader and must make sense unchanged to a 70-year-old.
Readability limits are set in the contract.

D7. Every item names a public-domain IPIP source item and a BFI-2 facet. At most four stems use Pokémon
flavour, and no item needs Pokémon knowledge.

D8. Topics that are too personal are banned: health, the body, money, sex, religion, politics, family
conflict, grief, school or work performance, and fears or sadness.

D9. The result is the nearest pool member in trait space, never a type. The result screen also shows the
taker's five trait positions.

D10. The result text never claims permanence, truth or scientific certainty, and presents the match as a
reading of today's answers.

D11. Every result quotes two of the taker's own answers, and every profile sentence carries a
species-specific anchor. Stock Barnum lines are banned, and no profile sentence is reused.

D12. The quiz makes no claim of validated measurement. Its expected instability on retakes is stated in
the contract and is not hidden from the check.

## Sources

| # | Source | URL | Read this session |
|---|---|---|---|
| 1 | Goldberg, L. R. (1990). An alternative "description of personality": The Big-Five factor structure. JPSP 59, 1216-1229. | https://doi.org/10.1037/0022-3514.59.6.1216 | no, cited from the record |
| 2 | McCrae, R. R., & Costa, P. T. (1997). Personality trait structure as a human universal. American Psychologist 52, 509-516. Also McCrae & Costa (1989), Reinterpreting the MBTI from the perspective of the five-factor model, J. Personality 57, 17-40. | https://doi.org/10.1037/0003-066X.52.5.509 and https://doi.org/10.1111/j.1467-6494.1989.tb00759.x | no, cited from the record |
| 3 | Soto, C. J. (2019). How replicable are links between personality traits and consequential life outcomes? Psychological Science 30, 711-727. | https://journals.sagepub.com/doi/abs/10.1177/0956797619831612 | abstract |
| 4 | Ashton, M. C., & Lee, K. (2007). Empirical, theoretical, and practical advantages of the HEXACO model. PSPR 11, 150-166. | https://journals.sagepub.com/doi/10.1177/1088868306294907 | abstract |
| 5 | Gosling, S. D., Rentfrow, P. J., & Swann, W. B. (2003). A very brief measure of the Big-Five personality domains. JRP 37, 504-528. | https://gosling.psy.utexas.edu/wp-content/uploads/2014/09/JRP-03-tipi.pdf | full text |
| 6 | Rammstedt, B., & John, O. P. (2007). Measuring personality in one minute or less: A 10-item short version of the BFI. JRP 41, 203-212. | https://www.sciencedirect.com/science/article/abs/pii/S0092656606000195 | abstract and summary |
| 7 | Donnellan, M. B., Oswald, F. L., Baird, B. M., & Lucas, R. E. (2006). The Mini-IPIP scales. Psychological Assessment 18, 192-203. | https://doi.org/10.1037/1040-3590.18.2.192 | abstract |
| 8 | Soto, C. J., & John, O. P. (2017). Short and extra-short forms of the Big Five Inventory-2: The BFI-2-S and BFI-2-XS. JRP 68, 69-81. | https://www.colby.edu/wp-content/uploads/2013/08/Soto_John_2017b.pdf | full text |
| 9 | Credé, M., Harms, P., Niehorster, S., & Gaye-Valentine, A. (2012). An evaluation of the consequences of using short measures of the Big Five personality traits. JPSP 102, 874-888. | https://pubmed.ncbi.nlm.nih.gov/22352328/ | abstract |
| 10 | Soto, C. J., John, O. P., Gosling, S. D., & Potter, J. (2008). The developmental psychometrics of Big Five self-reports: Acquiescence, factor structure, coherence, and differentiation from ages 10 to 20. JPSP 94, 718-737. | https://pubmed.ncbi.nlm.nih.gov/18361680/ | abstract |
| 11 | Marsh, H. W. (1986). Negative item bias in ratings scales for preadolescent children: A cognitive-developmental phenomenon. Developmental Psychology 22, 37-49. | https://psycnet.apa.org/record/1986-11523-001 | abstract |
| 12 | Borgers, N., & Hox, J. J. Reliability of responses in questionnaire research with children (secondary analysis); and Borgers, de Leeuw & Hox (2000), Children as respondents in survey research, BMS 66, 60-75. | https://www.joophox.net/papers/p021704.pdf and https://journals.sagepub.com/doi/abs/10.1177/075910630006600106 | full text (first), abstract (second) |
| 13 | Vicentini, Raccanello, & Burro (2025). Self-report questionnaires to measure Big Five personality traits in children and adolescents: A systematic review. Scandinavian Journal of Psychology 66, 627-653. | https://pmc.ncbi.nlm.nih.gov/articles/PMC12423744/ | full text |
| 14 | Brown, A., & Maydeu-Olivares, A. (2011). Item response modeling of forced-choice questionnaires. EPM 71, 460-502. | https://journals.sagepub.com/doi/10.1177/0013164410375112 | abstract |
| 15 | Cao, M., & Drasgow, F. (2019). Does forcing reduce faking? A meta-analytic review of forced-choice personality measures in high-stakes situations. JAP 104, 1347-1368. | https://gwern.net/doc/psychology/personality/2019-cao.pdf | abstract and summary |
| 16 | Shaffer, J. A., & Postlethwaite, B. E. (2012). A matter of context: A meta-analytic investigation of the relative validity of contextualized and noncontextualized personality measures. Personnel Psychology 65, 445-494. | https://onlinelibrary.wiley.com/doi/10.1111/j.1744-6570.2012.01250.x | abstract and summary |
| 17 | Game-like Personality Measure: McCord, Harman, & Purl (2019), Game-like personality testing, PAID; Harman (2025), Gamified personality assessment reduces faking and careless responding. | https://www.sciencedirect.com/science/article/abs/pii/S0191886919301266 and https://journals.sagepub.com/doi/full/10.1177/10711813251363208 | summaries only; author list of the 2019 paper cited from the record |
| 18 | Big Five Questionnaire for Children (Barbaranelli et al., 2003) and its Spanish validation, ages 8 to 15. | https://www.researchgate.net/publication/286515231_Big_five_questionnaire_dimensions_in_Spanish_children_BFQ-C | summary only |
| 19 | Pittenger, D. J. (2005). Cautionary comments regarding the Myers-Briggs Type Indicator. Consulting Psychology Journal 57, 210-221 (reports McCarley & Carskadon, 1983). | https://www.researchgate.net/publication/232494957_Cautionary_comments_regarding_the_Myers-Briggs_Type_Indicator | summary only |
| 20 | Tourangeau, R., & Yan, T. (2007). Sensitive questions in surveys. Psychological Bulletin 133, 859-883. | https://pubmed.ncbi.nlm.nih.gov/17723033/ | abstract |
| 21 | Clark, L. A., & Watson, D. (1995). Constructing validity: Basic issues in objective scale development. Psychological Assessment 7, 309-319. | https://doi.org/10.1037/1040-3590.7.3.309 | no, cited from the record |
| 22 | Forer, B. R. (1949). The fallacy of personal validation: A classroom demonstration of gullibility. JASP 44, 118-123. | https://www.researchgate.net/publication/5739334_The_fallacy_of_personal_validation_a_classroom_demonstration_of_gullibility | summary only |
| 23 | Dickson, D. H., & Kelly, I. W. (1985). The "Barnum effect" in personality assessment: A review of the literature. Psychological Reports 57, 367-382. | https://www.researchgate.net/publication/232554639_The_'Barnum_Effect'_in_Personality_Assessment_A_Review_of_the_Literature | summary only |
| 24 | Furnham, A., & Schofield, S. (1987). Accepting personality test feedback: A review of the Barnum effect. Current Psychology 6, 162-178. | https://link.springer.com/article/10.1007/BF02686623 | abstract |
| 25 | Pokémon of the Year 2020 results, top 30 (used for pool selection, not for psychology). | https://nintendosoup.com/these-are-top-30-pokemon-from-the-pokemon-of-the-year-poll/ and https://pokemon2020.pokemon.com/en-us/ | full text of the first |
