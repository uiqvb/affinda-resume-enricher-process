
Yes. And this was actually one of the most important turning points in our conversation.

Initially, I was suggesting products based on what sounded useful. You pushed back because we had no evidence that customers needed them or that Affinda wasn't already solving those problems.

Here's what I can reconstruct from our earlier discussion.

1. The ideas I suggested that you rejected
   Idea I proposed	What it would do	Why you rejected or questioned it
   Career Change Tracker	Analyse a candidate's employment history and detect career transitions, potentially for SEEK	Too specific to SEEK's internal recruitment workflows. We didn't know whether it was needed.
   Candidate Rediscovery	Help recruiters find previously overlooked candidates in their databases	Required access to customer data and systems we didn't have. Could already exist in an ATS.
   Generic Resume Validator	Identify missing, inconsistent or suspicious fields after Affinda parses a resume	Affinda Extract already offers validation and human-review capabilities. Not sufficiently differentiated.
   Human Review Dashboard	Give recruiters a UI to manually verify questionable extraction results	Largely duplicates existing document-processing workflows.
   Skills Normalisation Tool	Standardise extracted skill names for recruitment matching	Affinda already performs skill extraction and normalisation.
   Work-History Robustness Fixes	Improve the handling of complex employment histories and dates	We hadn't established that the parser actually struggled with them.
   Parser Upgrade Guard	Compare outputs from different parser versions to detect regressions before enterprise upgrades	Technically plausible, but we hadn't verified that the versions differed meaningfully or that customers needed a separate tool.
   Generic Operations Dashboard	Monitor extraction accuracy, errors and operational performance	Too broad, and potentially redundant with existing enterprise tooling.

These were explored ideas, not eight fully developed product proposals. Some were only briefly considered.
2. What you correctly challenged
Your objections followed a consistent pattern.

First: "Does Affinda already do this?"

You didn't want to spend four days reproducing functionality that Affinda already sells.

Second: "How do we know customers need this?"

Ideas like candidate rediscovery sounded useful, but we had no customer evidence.

Third: "How can we build this without internal access?"

Some concepts required SEEK's databases, hiring workflows or Affinda's proprietary infrastructure.

Fourth: "Where's the proof this is a problem?"

This was your most important criticism. We were discussing possible solutions before establishing that the problems existed.
3. Then you proposed a better approach
Your central suggestion was essentially:

"Why don't we actually test Affinda's API, find out what it struggles with, and build something that fixes a real issue?"

That reversed the entire process.
My initial approach
Invent product idea

Assume there's a need

Start building

Your proposed approach
Test actual API

Find reproducible gaps

Build a measured fix

4. What happened because of your suggestion
5. Round 1 — 30 resumes

   We explored the parser broadly, including hidden content, AI-directed instructions, difficult layouts, dates and contradictions.

   This produced the initial VisibleProof idea and several possible extraction issues.
6. Round 2 — 45 resumes

   You wanted to verify the initial failures rather than build immediately.

   We confirmed education-status information loss, narrowed the employment-date issue and failed to reproduce the employer-attribution problem.
7. Round 3 — 48 resumes

   You suggested exploring entirely different failure classes.

   This uncovered negated-skill extraction, certification-status limitations and some employment-type misclassifications.
8. Round 4 — 60 tests planned

   You wanted another round specifically to confirm or rule out the new findings before adding anything else to the wrapper.
9. The distinction that matters for your internship
   There are two different stories you could tell Andrew Bird.

A weaker story:

"I came up with several ideas for features Affinda could build."

Your actual story:

"I initially considered multiple potential extensions, but realised they were speculative or duplicated existing capabilities. So I designed an evaluation framework, tested 123 synthetic resumes against Affinda's actual parser, falsified several hypotheses, identified reproducible limitations, and designed targeted improvements."

That is substantially more convincing.

It demonstrates problem selection, experimental design, critical reasoning, and the willingness to abandon weak ideas.

And to be clear about credit: the decision to stop speculating and start testing was your contribution to the direction of this project. My initial brainstorming was broader and less evidence-based than it should have been.

The remaining challenge is to turn that rigorous investigation into a working implementation and demonstrate that your fixes generalise beyond the tests used to develop them.
