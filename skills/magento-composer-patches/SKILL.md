---
name: magento-composer-patches
description: Create or revise Composer-managed Magento 2 vendor patches, including patch ordering, regeneration and sequential verification. Excludes Magento setup data and schema patches.
---

# Magento 2 Patch Guidelines

1. **Read the repository policy and classify the change.** If `docs/composer-patches.md` exists, read it before editing and treat it as authoritative for repository-specific patch categories, application order and branch landing order. Inspect the locked package, registered patches and their application order. Distinguish defects in the original module from project-specific customisations and defects introduced by those customisations.

2. **Keep module bug fixes standalone and first.** Register module bug-fix patches before customisation patches for the same package. Each module bug-fix patch must apply independently to the clean, locked package and contain only the changes needed to fix that module defect. It must not depend on project customisations or another local patch. Keep it suitable for submission to the module developers.

3. **Order dependent work deliberately.** Follow the repository policy when it defines patch categories or ordering. Otherwise, place independently applicable and vendor-neutral changes before integrations that depend on project-specific modules, data or behavior. When work is split across branches, land the branches in final patch application order so each later patch is generated once against its completed baseline.

4. **Revise the existing patch for the same concern.** When changing an existing customisation or fixing a defect it introduced, update the patch that owns it. Likewise, revise the existing bug-fix patch when correcting or completing the same module fix. Do not add another patch merely to correct or extend an existing patch. Separate plans and branches do not require separate patch files. If an existing patch mixes a module bug fix with customisation, extract the module fix into a standalone patch and rebuild the customisation to follow it.

5. **Separate distinct concerns.** Create a new patch for an independent module bug fix or customisation when no existing patch suitably owns the change. Give it a clear, descriptive name. Do not bundle project-specific behavior into a module bug fix.

6. **Use the correct baseline.** Generate standalone module bug-fix patches against clean, locked package sources. Generate customisation patches against the locked package with all preceding registered patches applied, including module bug fixes. Never generate a revised patch against its own previously patched output. Rebuild affected later patches whenever an earlier patch changes or moves. Resolve overlaps while preserving both standalone bug-fix applicability and the full application sequence.

7. **Keep the diff narrow and maintain registration.** Preserve unrelated behavior. Exclude formatting churn, generated files and local configuration. Changes made only in `vendor/` are not deliverables. Follow repository conventions for paths, strip depth and Composer metadata. Preserve locked versions and references unless an upgrade is authorized.

8. **Verify independently and in sequence.** Verify each module bug-fix patch against a separate clean copy of the locked package, without other local patches. Then apply all registered patches in order to clean, locked sources. Investigate rejected hunks, fuzz and unexpected offsets. Compare the resulting code with the intended change; run relevant syntax and behavior checks. For module fixes, reproduce the original defect and verify the fix without project customisations. Preserve required diff context whitespace.

9. **Prepare module fixes for upstream reporting.** Provide the affected package and locked version, a concise defect description, reproduction steps or a regression test, expected and actual behavior, and verification results alongside the standalone patch. State any verification limitations. Preparing these materials does not imply submitting them to the module developers.

Report which patches changed, why any new patch was needed, the final application and branch landing order, and what independent and full-sequence verification passed.
