============
Code Reviews
============

All Kolla code must be reviewed and approved before it can be merged. Anyone
with a Gerrit account is able to provide a review. Two labels are available to
everyone:

* +1: Approve
* -1: Changes requested

It is also possible to leave comments without a label. In general, a review
with comments is more valuable. Comments are especially important for a
negative review. Prefer quality of reviews over quantity.

You can watch specific patches in Gerrit via *Settings -> Watched Projects*.
The volume of emails is not too large if you subscribe to *New Changes* only.
If you do not have much time available for reviewing, consider reviewing
patches in an area that is important to you or that you understand well.

Core reviewers
==============

Core reviewers have additional labels available to them.

* +2: Approve
* -2: Do not merge
* Workflow +1: Approve and ready for merge

Zuul requires one +2 and one workflow +1, as well as a passing check, in order
for a patch to proceed to the gate. The Kolla team generally requires two +2s
before a workflow +1 may be added. We also have some non-voting Zuul jobs which
will not block a check, but should be investigated if they are failing.

Core reviewers may still use +1 to indicate approval if they are not confident
enough about a particular patch to use +2.

The Kolla core reviewers have the same rights of access to stable branches, so
always check the branch for a review, and use extra care with stable branches.

Becoming a core reviewer
------------------------

There are no strict rules for becoming a core reviewer. Join the community,
review some patches, and demonstrate responsibility, understanding & care. If
you are interested in joining the core team, ask the PTL or another core
reviewer how to get there.
