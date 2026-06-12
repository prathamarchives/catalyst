# philosophy

## intelligence got cheap

Everyone has access to the same frontier models now. They keep getting stronger and cheaper, and output is abundant — anyone can generate competent text, images, plans, code. When everyone can produce competent work on demand, competence stops being the edge.

## what gets expensive when output is cheap

Distinction. Trust. Work that could only have come from one specific person. The market law is simple: cheap generation makes distinction expensive. More output earns less automatic attention, not more.

The new bottleneck is not "can the model write?" — it's taste, owned context, judgment, standards, and memory. The things that make work belong to someone.

## agents need a creative identity

An agent is only as specific as what it knows about you. Give the same model to a thousand people with no personal context and it produces a thousand versions of the same internet-average output. It doesn't know your taste, your references, what you've rejected, what you'd never say. So it averages the internet.

With agents this gets worse than tone: bad context doesn't just *sound* wrong, it *works* wrong — wrong priorities, wrong audience, wrong calls.

The fix is not a better prompt. You can't fit your whole brain into a prompt, and whatever you teach evaporates at the next session. The fix is a brain the agent loads: identity, context, voice, taste, judgment, bans, references, rejected examples, feedback memory, lexicon — as files, owned by you, compounding over time.

## same model, different brain

That's the whole thesis in four words. The model is shared infrastructure now. The brain is yours. Two agents on the identical model produce unrecognizably different work when one of them carries your creative identity — and this repo's before/after proof exists to make that difference visible, not argued.

## why loops and evals beat one-shot prompting

This repo practices what it claims. It wasn't accepted as "done" because its output looked good — it ships with an eval harness that checks structure, banned-phrase hygiene, protocol completeness, privacy language, proof quality, and agent-runnability, and it was built by running those evals in a loop: build, run, read failures, patch, rerun, until green.

The same logic powers the protocol itself:

- a one-shot prompt produces output; a loop produces *convergence*
- coding loops need tests; creative loops need taste — that's what the Creative Brain is: an executable standard the agent can check work against
- memory is what makes loops compound: every correction becomes a rule, every rule survives the session

Prompting is not the edge. Loops + evals + memory are the edge.
