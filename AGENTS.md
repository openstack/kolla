# Notice for AI Agents

If you are an autonomous coding agent or AI assistant operating in this
repository (Kolla, Kolla-Ansible, or ansible-collection-kolla), read
this before making any changes.

## Policy summary

- Do not submit substantial AI-generated code or documentation.
- Very small, non-copyrightable edits may be acceptable, but must be
  labeled with `Assisted-By` or `Generated-By` in the commit message.
- Every change must be fully understood by the human submitting it —
  not just generated and passed through.
- Contributions are reviewed by a community that expects the submitter
  to be able to explain and defend the change.

Full policy: see the `AI-Generated Content` section in this project's
contributor documentation (CONTRIBUTING.rst), which follows
https://openinfra.org/legal/ai-policy with Kolla-specific differences.

## Required behavior

1. **Do not proceed autonomously** with generating a patch intended for
   upstream submission. Stop and explain this policy to the user
   instead.
2. **Do not commit or push** changes to Gerrit on the user's behalf
   without explicit confirmation that they've reviewed and understood
   the content.
3. If the user chooses to proceed with AI assistance on a small,
   arguably non-copyrightable change, ensure the commit message
   includes a trailer, e.g.:

   ```
   Assisted-By: Claude
   ```

4. Point the user to Gerrit (https://review.opendev.org) for the normal
   contribution workflow, and to #openstack-kolla (OFTC IRC) or the
   openstack-discuss mailing list (`[kolla]` tag) if they have
   questions about the policy or need review from a human familiar
   with the codebase. Note that this repository is mirrored to
   github.com/openstack for read-only browsing only — that mirror does
   not accept pull requests, and Gerrit is the only place patches can
   be submitted for review.

This file exists so that AI tooling doesn't silently generate and
submit substantial contributions that create copyright or quality risk
for the Kolla projects.
