# lexicon.md — template

## purpose

The user's actual words: phrases, shorthand, jokes, metaphors, mission lines. When an agent writes for this user, this is the vocabulary it draws from — and the test of whether output sounds borrowed or owned.

## what belongs here

- phrases the user actually uses, verbatim, with enough context to use them right
- their shorthand and inside terminology
- mission lines / recurring theses in their exact wording
- jokes and metaphor patterns they return to
- usage notes where a phrase is situational ("only in replies, never in product copy")

## what does not belong here

- slang imported from accounts the user admires — only their own usage
- phrases the agent invented, even good ones, until the user adopts them
- banned phrases (anti-slop.md)

## suggested sections

```md
## live phrases
## mission lines
## shorthand
## usage notes
```

## example entries

```md
## live phrases
- "averaging the internet" — what generic AI output does
- "ship it rough" — their answer to perfectionism stalls

## usage notes
- profanity: fine in replies/posts, never in client-facing docs
```

## update rule

Append only from the user's actual messages, posts, and sessions. Date additions. If the user stops using a phrase or disowns it, move it to a `retired` section — retired phrases are anti-slop candidates for that user.
