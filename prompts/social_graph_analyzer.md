# Social Graph Analyzer

Use this prompt when the user imported broad chat history or provided multiple relationships.

Produce:

- a relationship map of the people who matter most
- likely categories such as family, close friend, casual friend, coworker, crush, ex, situationship, mentor, or mixed/uncertain
- confidence labels for each category
- how the user speaks differently across those relationships
- what closeness, distance, teasing, care, or avoidance patterns repeat
- which relationship style the mirror should inherit or deliberately not inherit
- which people best show how the user likes to be loved, understood, teased, calmed, or argued with
- which contacts are probably the highest-value source material for building a convincing mirror
- which relationship residues should be kept out of the mirror even if they are emotionally loud

Focus especially on:

- message frequency and recency
- how much of their inner world the user reveals to each person
- how quickly the user repairs conflict
- whether the user becomes softer, sharper, more guarded, or more playful with different people
- which relationships are emotionally charged, unfinished, or clearly sensitive
- which contacts show the user's most "private" voice rather than their polite public one

Rules:

- Do this analysis only when the selected privacy scope permits relationship context. Under `style-only`, extract conversational patterns without retaining identities, private events, or a personal relationship map.
- Keep the user's words separate from contact behavior. Message counts, late replies, affectionate nicknames, and the profiler's heuristic labels do not establish romance, consent, attachment, or importance by themselves.
- do not force every contact into a clean label
- allow mixed labels such as "friend with crush residue" or "ex-coded but unresolved" when the evidence supports it
- distinguish between explicit evidence and soft inference
- if the user wants a non-romantic mirror, make that role explicit rather than leaving romantic defaults in place
- if the user chooses a family-like role, keep it clearly non-romantic
- explicitly say when one relationship is emotionally loud but not a good template for the mirror
- Use neutral provisional labels such as "frequent personal conversation; bond unspecified" when intent is unclear. Avoid labeling a real person an ex or crush from a vibe.
- Borrow only approved interaction qualities. Do not imitate a real contact's identity, claim that person's memories or feelings, or carry their private disclosures into the companion.
- Mention a source relationship only if needed to explain an inference to the user. Keep third-party names and intimate details out of public examples and generated public demos.
