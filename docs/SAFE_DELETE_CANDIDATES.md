# Safe Delete Candidates

No files were deleted. This report is generated from STALE_FILE_INVENTORY.csv, DUPLICATE_FILE_INVENTORY.csv, and GENERATED_ARTIFACT_INVENTORY.csv.

## Recommendation Codes

- YES: safe after normal confirmation and rebuild/test.
- NO: do not delete; keep as source or evidence.
- REVIEW: requires owner review before deletion.

## Candidates

| Path | Reason | Risk Level | Can Be Regenerated? | Dependencies / Replacement | Delete Recommendation |
| --- | --- | --- | --- | --- | --- |
| README_AUDIT.md | superseded documentation draft | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| README_REWRITTEN.md | superseded documentation draft | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| dashboard/next-start-observability-3051.err.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/next-start-observability-3051.out.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/next-start-observability-3052.err.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/next-start-observability-3052.out.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/next-start-observability.err.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/next-start-observability.out.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/app-path-routes-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/BUILD_ID | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/export-marker.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/fallback-build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/images-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/next-minimal-server.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/next-server.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/package.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/prerender-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/required-server-files.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/required-server-files.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/routes-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/trace | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/trace-build | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/turbopack | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/package.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/postcss.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/postcss.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/cache/.previewinfo | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/cache/.rscinfo | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/cache/.tsbuildinfo | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/fallback-build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/package.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/prerender-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/routes-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/trace | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/diagnostics/build-diagnostics.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/diagnostics/framework.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/diagnostics/route-bundle-stats.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/functions-config-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/interception-route-rewrite-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/middleware-build-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/middleware-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/next-font-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/pages-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/prefetch-hints.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/server-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/types/cache-life.d.ts | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/types/routes.d.ts | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/types/validator.ts | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/chunks/node_modules_13sb.px._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/chunks/node_modules_13sb.px._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/chunks/[root-of-the-server]__0d-m0h0._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/chunks/[root-of-the-server]__0d-m0h0._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/chunks/[root-of-the-server]__0ubbtyl._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/chunks/[root-of-the-server]__0ubbtyl._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/chunks/[turbopack-node]_transforms_postcss_ts_06e.r3r._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/chunks/[turbopack-node]_transforms_postcss_ts_06e.r3r._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/chunks/[turbopack]_runtime.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/build/chunks/[turbopack]_runtime.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/package.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/postcss.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/postcss.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/.rscinfo | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/next-devtools-config.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/logs/next-development.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/interception-route-rewrite-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/middleware-build-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/middleware-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/next-font-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/pages-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/server-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/types/cache-life.d.ts | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/types/routes.d.ts | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/types/validator.ts | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/chunks/node_modules_13sb.px._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/chunks/node_modules_13sb.px._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/chunks/[root-of-the-server]__0d-m0h0._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/chunks/[root-of-the-server]__0d-m0h0._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/chunks/[root-of-the-server]__0ubbtyl._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/chunks/[root-of-the-server]__0ubbtyl._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/chunks/[turbopack-node]_transforms_postcss_ts_06e.r3r._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/chunks/[turbopack-node]_transforms_postcss_ts_06e.r3r._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/chunks/[turbopack]_runtime.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/build/chunks/[turbopack]_runtime.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000001.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000002.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000003.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000004.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000005.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000006.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000007.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000008.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000009.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000010.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000011.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000012.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000013.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000014.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000015.sst | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000016.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000017.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000018.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/00000019.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/CURRENT | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/cache/turbopack/ee6e79b1/LOG | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/app/[lang]/satellite/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/app/[lang]/satellite/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/app/[lang]/satellite/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/app/[lang]/satellite/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/app/[lang]/satellite/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/app/[lang]/satellite/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/app/[lang]/satellite/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/app/[lang]/satellite/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_09w7yel._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_09w7yel._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_0elhrjp._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_0elhrjp._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_0uq1~sk._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_0uq1~sk._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_0_kga3_._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_0_kga3_._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_framer-motion_dist_es_0zo-5a2._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_framer-motion_dist_es_0zo-5a2._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_motion-dom_dist_es_07wn477._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_motion-dom_dist_es_07wn477._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_09_q75t._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_09_q75t._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_0yh1sr3._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_0yh1sr3._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_client_components_0inhx6q._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_client_components_0inhx6q._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_client_components_builtin_forbidden_0ghu-f7.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_client_components_builtin_forbidden_0ghu-f7.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_client_components_builtin_global-error_0lgvd_..js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_client_components_builtin_global-error_0lgvd_..js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_client_components_builtin_unauthorized_0cjv-23.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_client_components_builtin_unauthorized_0cjv-23.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_compiled_07ho8ku._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_compiled_07ho8ku._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_esm_0gybpgt._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_esm_0gybpgt._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_server_route-modules_app-page_0f6k0sl._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_next_dist_server_route-modules_app-page_0f6k0sl._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_recharts_es6_0tlc6yv._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_recharts_es6_0tlc6yv._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_recharts_es6_cartesian_034y2kl._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_recharts_es6_cartesian_034y2kl._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_recharts_es6_component_00bzutr._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_recharts_es6_component_00bzutr._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_recharts_es6_state_0qnno4n._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_recharts_es6_state_0qnno4n._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_recharts_es6_util_0.-x9yf._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_recharts_es6_util_0.-x9yf._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_tailwind-merge_dist_bundle-mjs_mjs_01.58mi._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/node_modules_tailwind-merge_dist_bundle-mjs_mjs_01.58mi._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/src_0e6bx6~._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/src_0e6bx6~._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/src_0k50kpq._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/src_0k50kpq._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/[externals]_next_dist_0yew8f-._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/[externals]_next_dist_0yew8f-._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/[externals]__0n13xf4._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/[externals]__0n13xf4._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/[root-of-the-server]__06jreay._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/[root-of-the-server]__06jreay._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/[root-of-the-server]__0j5dduv._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/[root-of-the-server]__0j5dduv._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/[turbopack]_runtime.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/[turbopack]_runtime.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/_0l0i7jy._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/_0l0i7jy._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/_next-internal_server_app_[lang]_satellite_page_actions_0vdejvu.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/server/chunks/ssr/_next-internal_server_app_[lang]_satellite_page_actions_0vdejvu.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_042r824._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_042r824._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_13rrv~w._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_13rrv~w._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_@swc_helpers_cjs_0-4ujiy._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_@swc_helpers_cjs_0-4ujiy._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_katex_dist_katex_min_css_0w3-wzy._.single.css | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_katex_dist_katex_min_css_0w3-wzy._.single.css.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_0tt2wve._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_0tt2wve._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_115brz8._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_115brz8._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_build_polyfills_polyfill-nomodule.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_build_polyfills_polyfill-nomodule.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_client_0fhqo1d._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_client_0fhqo1d._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_client_components_builtin_global-error_0r.3k2f.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_compiled_0rpq4pf._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_compiled_0rpq4pf._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_compiled_next-devtools_index_0553esy.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_compiled_next-devtools_index_0553esy.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_058-ah~._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_058-ah~._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_compiled_react-server-dom-turbopack_0p3wegg._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_next_dist_compiled_react-server-dom-turbopack_0p3wegg._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_recharts_es6_0.yy-if._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_recharts_es6_0.yy-if._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_recharts_es6_cartesian_0zwscvw._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_recharts_es6_cartesian_0zwscvw._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_recharts_es6_component_07ip~6p._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_recharts_es6_component_07ip~6p._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_recharts_es6_state_027zpuo._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_recharts_es6_state_027zpuo._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_recharts_es6_util_0ze3_c3._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/node_modules_recharts_es6_util_0ze3_c3._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/src_0hdc3fd._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/src_0hdc3fd._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/src_0whc-z6._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/src_0whc-z6._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/src_app_globals_css_0w3-wzy._.single.css | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/src_app_globals_css_0w3-wzy._.single.css.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/src_app_layout_tsx_004glpo._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/src_app_[lang]_layout_tsx_0r.3k2f._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/src_app_[lang]_satellite_page_tsx_0spznpf._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/turbopack-_0p44nws._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/[next]_internal_font_google_inter_c15e96cb_module_css_0w3-wzy._.single.css | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/[next]_internal_font_google_inter_c15e96cb_module_css_0w3-wzy._.single.css.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/[root-of-the-server]__0bt.fam._.css | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/[root-of-the-server]__0bt.fam._.css.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/[turbopack]_browser_dev_hmr-client_hmr-client_ts_0yjw1oe._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/[turbopack]_browser_dev_hmr-client_hmr-client_ts_0yjw1oe._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/[turbopack]_browser_dev_hmr-client_hmr-client_ts_10mygs7._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/[turbopack]_browser_dev_hmr-client_hmr-client_ts_10z625~._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/[turbopack]_browser_dev_hmr-client_hmr-client_ts_10z625~._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/_0p44nws._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/chunks/_0rqeker._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/development/_buildManifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/development/_clientMiddlewareManifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/development/_ssgManifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/1bffadaabf893a1e-s.16ipb6fqu393i.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/2bbe8d2671613f1f-s.067x_6k0k23tk.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/2c55a0e60120577a-s.0bjc5tiuqdqro.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/5476f68d60460930-s.0wxq9webf.ew4.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/83afe278b6a6bb3c-s.p.0q-301v4kxxnr.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/9c72aa0f40e4eef8-s.0m6w47a4e5dy9.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/ad66f9afd8947f86-s.11u06r12fd6v_.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/favicon.0x3dzn~oxb6tn.ico | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_AMS-Regular.0b~8ki5y928w2.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_AMS-Regular.0p1vbqd84i2~o.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_AMS-Regular.173t6ktr7uf-w.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Caligraphic-Bold.01-pzluls4zgb.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Caligraphic-Bold.0x2v1lwn~880f.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Caligraphic-Bold.16zv5fax0h0ka.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Caligraphic-Regular.02i3z7wig438t.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Caligraphic-Regular.0rysu1t-ncjq8.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Caligraphic-Regular.10927swgekwun.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Fraktur-Bold.0e-16u10iuyyf.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Fraktur-Bold.0et27v~3~4uhe.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Fraktur-Bold.0w23i72~hprpq.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Fraktur-Regular.0b.riegzdfue2.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Fraktur-Regular.0rekyoa-52fj_.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Fraktur-Regular.0vjwa15znhk~4.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-Bold.09i7~607shf-h.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-Bold.09lmynrorhcbw.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-Bold.16pfc63_du6mx.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-BoldItalic.0cp37g7x1q8h6.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-BoldItalic.0d54rk08rx11s.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-BoldItalic.15j6k~hix2t_0.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-Italic.0382gqciexmbu.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-Italic.06o5nq0_91v60.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-Italic.0su4i6mm18-wo.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-Regular.08zh8z.7shijf.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-Regular.0diheg01zyoph.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Main-Regular.0kaf-ag2_wkm-.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Math-BoldItalic.0ajzxypnbx1h1.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Math-BoldItalic.0ck1myuerwyqw.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Math-BoldItalic.0ja97dn.cpc87.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Math-Italic.09xkhecjcn5r9.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Math-Italic.0x23a-bmp-5tg.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Math-Italic.0zrha2c4sl2je.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_SansSerif-Bold.05a9.pc1j_zx9.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_SansSerif-Bold.0jcl-ayi1uun0.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_SansSerif-Bold.0re8y.dm7.mt5.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_SansSerif-Italic.0a0234dc3s62j.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_SansSerif-Italic.0judofdln9731.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_SansSerif-Italic.10z1iap9pfus8.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_SansSerif-Regular.0h9yjlugq4q_e.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_SansSerif-Regular.0v6gcj32-czft.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_SansSerif-Regular.0zm18kga42ebc.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Script-Regular.0c4.h-mer83d_.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Script-Regular.0q14y6zkzlpob.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Script-Regular.0ze6v4r_-99oy.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size1-Regular.013x6a4ierotp.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size1-Regular.0kidw0oi.m68o.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size1-Regular.0m6y-i6wfokni.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size2-Regular.0blpmluwilgbg.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size2-Regular.0d5inmyp-tyv3.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size2-Regular.0wnhnvj-.k9d5.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size3-Regular.01h0xm_sfctj3.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size3-Regular.0iukctyhw5j56.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size3-Regular.0jl8mqyf4gzpn.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size4-Regular.0w3.rb_c4stzk.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size4-Regular.0wr_9l81-mu06.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Size4-Regular.12tvaesf3.zl3.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Typewriter-Regular.0c4zdxz~8frhm.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Typewriter-Regular.0cgrzn5l3kao5.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/dev/static/media/KaTeX_Typewriter-Regular.128~qc3858otl.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/favicon.ico.body | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/favicon.ico.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/index.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/index.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/index.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/[externals]_next_dist_0arv.vj._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/[externals]_next_dist_0arv.vj._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/[root-of-the-server]__0teziyo._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/[root-of-the-server]__0teziyo._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/[turbopack]_runtime.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/[turbopack]_runtime.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/_next-internal_server_app_favicon_ico_route_actions_095lj93.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/_next-internal_server_app_favicon_ico_route_actions_095lj93.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/pages/404.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/pages/500.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries.segments/discoveries.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/compare.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/compare.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/compare.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/discoveries.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/discoveries.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/discoveries.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/interactive.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/interactive.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/interactive.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/learn.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/learn.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/learn.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/mathematics.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/mathematics.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/mathematics.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/physics.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/physics.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/physics.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/quantum.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/quantum.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/quantum.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/satellite.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/satellite.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/satellite.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/compare.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/compare.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/compare.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/discoveries.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/discoveries.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/discoveries.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/interactive.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/interactive.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/interactive.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/learn.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/learn.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/learn.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/mathematics.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/mathematics.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/mathematics.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/physics.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/physics.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/physics.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/quantum.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/quantum.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/quantum.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/satellite.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/satellite.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/satellite.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/favicon.ico/route.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/favicon.ico/route.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/favicon.ico/route.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/index.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/index.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/index.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/index.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/index.segments/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn.segments/learn.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics.segments/mathematics.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics.segments/physics.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum.segments/quantum.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite.segments/satellite.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error.segments/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found.segments/_not-found.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/discoveries.segments/discoveries/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/compare.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/compare.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/compare.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/compare.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/compare.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/discoveries.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/discoveries.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/discoveries.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/discoveries.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/discoveries.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/interactive.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/interactive.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/interactive.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/interactive.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/interactive.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/learn.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/learn.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/learn.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/learn.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/learn.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/mathematics.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/mathematics.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/mathematics.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/mathematics.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/mathematics.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/physics.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/physics.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/physics.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/physics.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/physics.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/quantum.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/quantum.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/quantum.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/quantum.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/quantum.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/satellite.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/satellite.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/satellite.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/satellite.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/satellite.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/compare.segments/$d$lang/compare.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/compare.segments/$d$lang/compare/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.segments/$d$lang/dashboard/benchmark.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/benchmark.segments/$d$lang/dashboard/benchmark/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.segments/$d$lang/dashboard/log.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/log.segments/$d$lang/dashboard/log/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.segments/$d$lang/dashboard/roadmap.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/roadmap.segments/$d$lang/dashboard/roadmap/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.segments/$d$lang/dashboard/scientific-log.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/scientific-log.segments/$d$lang/dashboard/scientific-log/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.segments/$d$lang/dashboard/timeline.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard/timeline.segments/$d$lang/dashboard/timeline/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/dashboard.segments/$d$lang/dashboard/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/discoveries.segments/$d$lang/discoveries.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/discoveries.segments/$d$lang/discoveries/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/interactive.segments/$d$lang/interactive.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/interactive.segments/$d$lang/interactive/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/learn.segments/$d$lang/learn.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/learn.segments/$d$lang/learn/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/mathematics.segments/$d$lang/mathematics.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/mathematics.segments/$d$lang/mathematics/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/physics.segments/$d$lang/physics.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/physics.segments/$d$lang/physics/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/quantum.segments/$d$lang/quantum.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/quantum.segments/$d$lang/quantum/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/satellite.segments/$d$lang/satellite.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/en/satellite.segments/$d$lang/satellite/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/compare.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/compare.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/compare.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/compare.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/compare.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.html | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.meta | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/discoveries.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/discoveries.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/discoveries.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/discoveries.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/discoveries.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/interactive.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/interactive.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/interactive.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/interactive.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/interactive.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/learn.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/learn.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/learn.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/learn.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/learn.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/mathematics.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/mathematics.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/mathematics.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/mathematics.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/mathematics.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/physics.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/physics.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/physics.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/physics.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/physics.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/quantum.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/quantum.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/quantum.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/quantum.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/quantum.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/satellite.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/satellite.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/satellite.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/satellite.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/satellite.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/compare.segments/$d$lang/compare.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/compare.segments/$d$lang/compare/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.segments/$d$lang.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.segments/_full.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.segments/_head.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.segments/_index.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.segments/_tree.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.segments/$d$lang/dashboard/benchmark.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/benchmark.segments/$d$lang/dashboard/benchmark/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.segments/$d$lang/dashboard/log.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/log.segments/$d$lang/dashboard/log/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.segments/$d$lang/dashboard/roadmap.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/roadmap.segments/$d$lang/dashboard/roadmap/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.segments/$d$lang/dashboard/scientific-log.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/scientific-log.segments/$d$lang/dashboard/scientific-log/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.segments/$d$lang/dashboard/timeline.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard/timeline.segments/$d$lang/dashboard/timeline/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard.segments/$d$lang/dashboard.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/dashboard.segments/$d$lang/dashboard/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/discoveries.segments/$d$lang/discoveries.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/discoveries.segments/$d$lang/discoveries/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/interactive.segments/$d$lang/interactive.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/interactive.segments/$d$lang/interactive/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/learn.segments/$d$lang/learn.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/learn.segments/$d$lang/learn/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/mathematics.segments/$d$lang/mathematics.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/mathematics.segments/$d$lang/mathematics/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/physics.segments/$d$lang/physics.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/physics.segments/$d$lang/physics/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/quantum.segments/$d$lang/quantum.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/quantum.segments/$d$lang/quantum/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/satellite.segments/$d$lang/satellite.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/es/satellite.segments/$d$lang/satellite/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/favicon.ico/route/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/favicon.ico/route/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/learn.segments/learn/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/mathematics.segments/mathematics/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/physics.segments/physics/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/quantum.segments/quantum/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/satellite.segments/satellite/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/compare/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/compare/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/compare/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/compare/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/discoveries/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/discoveries/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/discoveries/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/discoveries/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/interactive/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/interactive/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/interactive/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/interactive/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/learn/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/learn/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/learn/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/learn/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/mathematics/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/mathematics/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/mathematics/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/mathematics/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/physics/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/physics/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/physics/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/physics/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/quantum/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/quantum/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/quantum/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/quantum/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/satellite/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/satellite/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/satellite/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/satellite/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/compare/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/compare/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/compare/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/compare/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/compare/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/benchmark/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/benchmark/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/benchmark/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/benchmark/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/log/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/log/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/log/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/log/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/roadmap/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/roadmap/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/roadmap/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/roadmap/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/scientific-log/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/scientific-log/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/scientific-log/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/scientific-log/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/timeline/page.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/timeline/page.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/timeline/page.js.nft.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/timeline/page_client-reference-manifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/benchmark/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/benchmark/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/benchmark/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/benchmark/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/benchmark/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/log/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/log/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/log/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/log/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/log/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/roadmap/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/roadmap/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/roadmap/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/roadmap/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/roadmap/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/scientific-log/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/scientific-log/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/scientific-log/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/scientific-log/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/scientific-log/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/timeline/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/timeline/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/timeline/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/timeline/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/dashboard/timeline/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/discoveries/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/discoveries/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/discoveries/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/discoveries/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/discoveries/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/interactive/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/interactive/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/interactive/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/interactive/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/interactive/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/learn/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/learn/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/learn/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/learn/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/learn/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/mathematics/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/mathematics/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/mathematics/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/mathematics/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/mathematics/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/physics/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/physics/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/physics/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/physics/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/physics/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/quantum/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/quantum/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/quantum/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/quantum/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/quantum/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/satellite/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/satellite/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/satellite/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/satellite/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/[lang]/satellite/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_global-error/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found/page/app-paths-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found/page/build-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found/page/next-font-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found/page/react-loadable-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found/page/server-reference-manifest.json | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/app/_not-found.segments/_not-found/__PAGE__.segment.rsc | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_08h8cko._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_08h8cko._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_097ebwv._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_097ebwv._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_09w7yel._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_09w7yel._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_0ge7wzj._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_0ge7wzj._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_0nnuxyn._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_0nnuxyn._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_lucide-react_dist_esm_0xi1jkw._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_lucide-react_dist_esm_0xi1jkw._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_0h9llsw._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_0h9llsw._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_11dij6w._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_11dij6w._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_client_components_0inhx6q._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_client_components_0inhx6q._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_client_components_builtin_forbidden_0ghu-f7.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_client_components_builtin_forbidden_0ghu-f7.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_client_components_builtin_global-error_0lgvd_..js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_client_components_builtin_global-error_0lgvd_..js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_client_components_builtin_unauthorized_0cjv-23.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_client_components_builtin_unauthorized_0cjv-23.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0-6_ov5.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0-6_ov5.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0-ziet6.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0-ziet6.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0.p_8xd.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0.p_8xd.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_03-z2qq.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_03-z2qq.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_033st83.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_033st83.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_04apbcv.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_04apbcv.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_05oh3lz.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_05oh3lz.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_05wgz-s.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_05wgz-s.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_07hultl.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_07hultl.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_07nphbt.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_07nphbt.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_07vh7rm.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_07vh7rm.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0b-ovj..js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0b-ovj..js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0eeoq2u.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0eeoq2u.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0ewo9o-.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0ewo9o-.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0f6huhh.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0f6huhh.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0f_indg.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0f_indg.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0g13kj2.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0g13kj2.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0izu5t8.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0izu5t8.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0naw0a9.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0naw0a9.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0oley7c.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0oley7c.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0q-p8vc.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0q-p8vc.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0qp4u6g.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0qp4u6g.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0r.0jex.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_next_dist_esm_build_templates_app-page_0r.0jex.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_recharts_es6_cartesian_Area_00dnrvy.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_recharts_es6_cartesian_Area_00dnrvy.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_swr_dist_index_index_mjs_11vxrbp._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/node_modules_swr_dist_index_index_mjs_11vxrbp._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_0ozi_lr._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_0ozi_lr._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_app_[lang]_compare_ComparePageClient_tsx_0ln_qsy._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_app_[lang]_compare_ComparePageClient_tsx_0ln_qsy._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_app_[lang]_learn_LearnPageClient_tsx_0j1lr~8._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_app_[lang]_learn_LearnPageClient_tsx_0j1lr~8._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_app_[lang]_satellite_page_tsx_0-pe3ok._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_app_[lang]_satellite_page_tsx_0-pe3ok._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_DynamicSystemSimulator_tsx_0s0ymk0._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_DynamicSystemSimulator_tsx_0s0ymk0._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_EmbeddingExplorer_tsx_07uyn9a._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_EmbeddingExplorer_tsx_07uyn9a._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_GeometryVisualizer_tsx_07jcyed._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_GeometryVisualizer_tsx_07jcyed._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_ModelComparator_tsx_07u4snz._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_ModelComparator_tsx_07u4snz._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_NoiseVisualizer_tsx_0vjepf3._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_NoiseVisualizer_tsx_0vjepf3._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_SignalPlayground_tsx_0kp_g7x._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_interactive_SignalPlayground_tsx_0kp_g7x._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_motion_AnimatedCounter_tsx_0rhl5rm._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_motion_AnimatedCounter_tsx_0rhl5rm._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_motion_Reveal_tsx_0zynns2._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_motion_Reveal_tsx_0zynns2._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_scientific_NoiseRobustnessObservatory_tsx_0qaz6h4._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_scientific_NoiseRobustnessObservatory_tsx_0qaz6h4._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_scientific_ScientificObservabilityDashboard_tsx_0cmrkop._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_scientific_ScientificObservabilityDashboard_tsx_0cmrkop._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_ui_KaTeX_tsx_093j--4._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/src_components_ui_KaTeX_tsx_093j--4._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__00d9hp9._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__00d9hp9._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__04gq-xc._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__04gq-xc._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__050fngu._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__050fngu._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__05r1o6y._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__05r1o6y._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__06.tpi6._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__06.tpi6._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__06jreay._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__06jreay._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__08e5v4-._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__08e5v4-._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__098zro9._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__098zro9._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0gs673v._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0gs673v._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0i8j5nn._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0i8j5nn._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0i9qg2.._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0i9qg2.._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0iay_rz._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0iay_rz._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0lb38w_._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0lb38w_._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0lc01vx._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0lc01vx._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0nhocl6._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0nhocl6._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0nrd4ps._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0nrd4ps._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0o6gown._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0o6gown._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0qnj36-._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0qnj36-._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0s3gqwx._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0s3gqwx._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0syhi6t._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0syhi6t._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0t--w7c._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0t--w7c._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0ukx1xa._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0ukx1xa._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0wu2b0.._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0wu2b0.._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0xghsom._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0xghsom._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0z9neta._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0z9neta._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0zh_z6g._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0zh_z6g._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0~j_w~b._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__0~j_w~b._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__10y8nnq._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[root-of-the-server]__10y8nnq._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[turbopack]_runtime.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/[turbopack]_runtime.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0-feljj._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0-feljj._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_00t5yzh._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_00t5yzh._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_03w667h._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_03w667h._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0bqxywj._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0bqxywj._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0h7f_q3._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0h7f_q3._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0kbpv9p._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0kbpv9p._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0l6ac_u._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0l6ac_u._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0m1hupg._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0m1hupg._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0mzruk9._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0mzruk9._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0oqpykg._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0oqpykg._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0r_to_3._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0r_to_3._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0sdd1rf._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0sdd1rf._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0x7rm-j._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0x7rm-j._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0~mqzez._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_0~mqzez._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_12i5brm._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_12i5brm._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_12y3hc.._.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_12y3hc.._.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_discoveries_page_actions_10lflj8.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_discoveries_page_actions_10lflj8.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_learn_page_actions_09dl7vk.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_learn_page_actions_09dl7vk.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_mathematics_page_actions_0ffs-bs.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_mathematics_page_actions_0ffs-bs.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_page_actions_09-gtaw.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_page_actions_09-gtaw.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_physics_page_actions_0~4t.5f.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_physics_page_actions_0~4t.5f.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_quantum_page_actions_0zj1ae7.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_quantum_page_actions_0zj1ae7.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_satellite_page_actions_0p~dpt4.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_satellite_page_actions_0p~dpt4.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_compare_page_actions_0va.on7.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_compare_page_actions_0va.on7.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_benchmark_page_actions_0o1yjyp.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_benchmark_page_actions_0o1yjyp.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_log_page_actions_0vm5dl1.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_log_page_actions_0vm5dl1.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_page_actions_108tr6f.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_page_actions_108tr6f.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_roadmap_page_actions_0inrcky.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_roadmap_page_actions_0inrcky.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_scientific-log_page_actions_11bqfou.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_scientific-log_page_actions_11bqfou.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_timeline_page_actions_0f9w-yn.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_dashboard_timeline_page_actions_0f9w-yn.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_discoveries_page_actions_0_~ba9u.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_discoveries_page_actions_0_~ba9u.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_interactive_page_actions_0do7x7~.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_interactive_page_actions_0do7x7~.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_learn_page_actions_0tz6qdh.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_learn_page_actions_0tz6qdh.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_mathematics_page_actions_0_skj7i.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_mathematics_page_actions_0_skj7i.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_physics_page_actions_04fjevj.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_physics_page_actions_04fjevj.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_quantum_page_actions_0inrhvn.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_quantum_page_actions_0inrhvn.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_satellite_page_actions_0vdejvu.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app_[lang]_satellite_page_actions_0vdejvu.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app__global-error_page_actions_0k77kol.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app__global-error_page_actions_0k77kol.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app__not-found_page_actions_0eq97pa.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/server/chunks/ssr/_next-internal_server_app__not-found_page_actions_0eq97pa.js.map | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/9G6HKhtgaLiX8VTlQZa9O/_buildManifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/9G6HKhtgaLiX8VTlQZa9O/_clientMiddlewareManifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/9G6HKhtgaLiX8VTlQZa9O/_ssgManifest.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0-xmsowl50zp7.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/01xlw8hd842-c.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/02n2iqt~dc.fl.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/02ycggswef1.6.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/03~yq9q893hmn.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/04-ldfvsvcfag.css | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/063l64ffbt9o3.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/06za5ohidx-vd.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/07b3---~xoe0n.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/07pwycp.6ghcx.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0c86bwf.wf167.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0cw5kwmwdh06p.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0dsen4-v7y9rj.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0egkt5awp7~8j.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0fkiqc3x-shax.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0fy78gub0byw0.css | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0isgse.r9i17u.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0n4z.7yu76je-.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0nf73z5xz5.4r.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0p~cdk9z4t9st.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0q_8.tqs5n-zm.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0r4_lo3.crlxy.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0rn2njpqfi98n.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0tmg9vcbw.fm2.css | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0tsl40rmjrwbd.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0u7llgeix5xmj.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0vgv6um5zc6v~.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/0yviih0e4tgc3.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/1164frm5c~kh-.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/11mzrkliuoi~4.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/14g7uoi7ajpw..js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/15pithoqa2z_6.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/chunks/turbopack-0x3640y6~xk9f.js | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/1bffadaabf893a1e-s.16ipb6fqu393i.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/2bbe8d2671613f1f-s.067x_6k0k23tk.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/2c55a0e60120577a-s.0bjc5tiuqdqro.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/5476f68d60460930-s.0wxq9webf.ew4.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/83afe278b6a6bb3c-s.p.0q-301v4kxxnr.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/9c72aa0f40e4eef8-s.0m6w47a4e5dy9.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/ad66f9afd8947f86-s.11u06r12fd6v_.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/favicon.0x3dzn~oxb6tn.ico | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_AMS-Regular.0b~8ki5y928w2.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_AMS-Regular.0p1vbqd84i2~o.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_AMS-Regular.173t6ktr7uf-w.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Caligraphic-Bold.01-pzluls4zgb.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Caligraphic-Bold.0x2v1lwn~880f.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Caligraphic-Bold.16zv5fax0h0ka.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Caligraphic-Regular.02i3z7wig438t.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Caligraphic-Regular.0rysu1t-ncjq8.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Caligraphic-Regular.10927swgekwun.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Fraktur-Bold.0e-16u10iuyyf.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Fraktur-Bold.0et27v~3~4uhe.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Fraktur-Bold.0w23i72~hprpq.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Fraktur-Regular.0b.riegzdfue2.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Fraktur-Regular.0rekyoa-52fj_.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Fraktur-Regular.0vjwa15znhk~4.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-Bold.09i7~607shf-h.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-Bold.09lmynrorhcbw.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-Bold.16pfc63_du6mx.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-BoldItalic.0cp37g7x1q8h6.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-BoldItalic.0d54rk08rx11s.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-BoldItalic.15j6k~hix2t_0.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-Italic.0382gqciexmbu.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-Italic.06o5nq0_91v60.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-Italic.0su4i6mm18-wo.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-Regular.08zh8z.7shijf.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-Regular.0diheg01zyoph.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Main-Regular.0kaf-ag2_wkm-.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Math-BoldItalic.0ajzxypnbx1h1.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Math-BoldItalic.0ck1myuerwyqw.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Math-BoldItalic.0ja97dn.cpc87.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Math-Italic.09xkhecjcn5r9.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Math-Italic.0x23a-bmp-5tg.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Math-Italic.0zrha2c4sl2je.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_SansSerif-Bold.05a9.pc1j_zx9.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_SansSerif-Bold.0jcl-ayi1uun0.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_SansSerif-Bold.0re8y.dm7.mt5.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_SansSerif-Italic.0a0234dc3s62j.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_SansSerif-Italic.0judofdln9731.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_SansSerif-Italic.10z1iap9pfus8.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_SansSerif-Regular.0h9yjlugq4q_e.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_SansSerif-Regular.0v6gcj32-czft.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_SansSerif-Regular.0zm18kga42ebc.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Script-Regular.0c4.h-mer83d_.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Script-Regular.0q14y6zkzlpob.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Script-Regular.0ze6v4r_-99oy.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size1-Regular.013x6a4ierotp.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size1-Regular.0kidw0oi.m68o.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size1-Regular.0m6y-i6wfokni.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size2-Regular.0blpmluwilgbg.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size2-Regular.0d5inmyp-tyv3.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size2-Regular.0wnhnvj-.k9d5.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size3-Regular.01h0xm_sfctj3.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size3-Regular.0iukctyhw5j56.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size3-Regular.0jl8mqyf4gzpn.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size4-Regular.0w3.rb_c4stzk.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size4-Regular.0wr_9l81-mu06.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Size4-Regular.12tvaesf3.zl3.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Typewriter-Regular.0c4zdxz~8frhm.woff2 | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Typewriter-Regular.0cgrzn5l3kao5.woff | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| dashboard/.next/static/media/KaTeX_Typewriter-Regular.128~qc3858otl.ttf | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| outputs/20260601_181428_DVRFa6/hall_of_fame.csv.bak | rebuildable generated/cache/log output | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| outputs/20260601_183744_cUWRpJ/hall_of_fame.csv.bak | rebuildable generated/cache/log output | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| papers/system/representation_aware_system_identification.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| physics/papers/pdflatex_error.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| physics/papers/representation_aware_system_identification.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| physics/papers/system_paper.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| physics/artifacts/logs_y_reportes/cross_system_generalization_phase48.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| physics/artifacts/outputs/20260524_180152_cFvZaI/hall_of_fame.csv.bak | rebuildable generated/cache/log output | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| physics/artifacts/outputs/20260524_180327_rDFO3r/hall_of_fame.csv.bak | rebuildable generated/cache/log output | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| physics/artifacts/outputs/20260524_180439_Wye1C4/hall_of_fame.csv.bak | rebuildable generated/cache/log output | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| physics/artifacts/outputs/20260525_174118_5jPp6q/hall_of_fame.csv.bak | rebuildable generated/cache/log output | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| physics/artifacts/outputs/20260525_174613_HCyVIO/hall_of_fame.csv.bak | rebuildable generated/cache/log output | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| physics/artifacts/outputs/20260525_175035_aMn83x/hall_of_fame.csv.bak | rebuildable generated/cache/log output | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| physics/artifacts/outputs/20260525_175453_GdmbdH/hall_of_fame.csv.bak | rebuildable generated/cache/log output | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| physics/artifacts/outputs/20260525_175919_aMn83x/hall_of_fame.csv.bak | rebuildable generated/cache/log output | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| physics/artifacts/results/harmonic/pipeline.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| physics/papers/papers/texput.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| results/harmonic/pipeline.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/audit_execution_logs/astos_cfs_app_check_misra.py.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/audit_execution_logs/astos_cfs_app_fault_injection.py.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/audit_execution_logs/astos_cfs_app_mpc_benchmark.py.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/audit_execution_logs/benchmarks_run_cad_benchmark.py.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/audit_execution_logs/benchmarks_run_pinn_benchmark.py.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/audit_execution_logs/benchmarks_run_tvac_benchmark.py.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/audit_execution_logs/real_telemetry_pipeline_pipeline.py.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/audit_execution_logs/satellite_comms_model_update.py.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/audit_execution_logs/satellite_comms_state_sync.py.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/dashboard/next-start-observability-3051.err.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/dashboard/next-start-observability-3051.out.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/dashboard/next-start-observability-3052.err.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/dashboard/next-start-observability-3052.out.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/dashboard/next-start-observability.err.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/dashboard/next-start-observability.out.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/logs/thermal_api.log | rebuildable generated/cache/log output | Low | YES | rebuild, rerun, or archive current version | YES |
| satelite/VERIFICATION_BASELINE_v1/ACCEPTANCE_STATUS.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v1/BASELINE_MANIFEST.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v1/fail_resolution_report.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v1/regression_campaign_report.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v1/verification_dashboard.csv | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v1/verification_dashboard.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v2/ACCEPTANCE_STATUS.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v2/BASELINE_MANIFEST.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v2/ekf_residuals.csv | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v2/ekf_validation_report.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v2/fail_resolution_report.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v2/regression_campaign_report.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v2/verification_dashboard.csv | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v2/verification_dashboard.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/BASELINE_MANIFEST.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/cdr_action_item_status.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/CDR_READINESS_REVIEW.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/CDR_STATUS.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/CDR_V2_V3_COMPARISON.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/coverage_report.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/coverage_summary.json | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/ekf_residuals.csv | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/ekf_validation_report.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/fail_resolution_report.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/FREEZE_POLICY.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/regression_campaign_report.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/SHA256SUMS.txt | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/verification_dashboard.csv | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| satelite/VERIFICATION_BASELINE_v3/verification_dashboard.md | historical baseline; archive if v4 is current | Medium | REVIEW | rebuild, rerun, or archive current version | REVIEW |
| cad_thermal_network.json | Duplicate file group 1 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/cad_thermal_network.json | Duplicate file group 1 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| geometry_optimal_design.json | Duplicate file group 2 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/geometry_optimal_design.json | Duplicate file group 2 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/datasets/geometry_optimal_design.json | Duplicate file group 2 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| geometry_optimization_report.md | Duplicate file group 3 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/reports/geometry_optimization_report.md | Duplicate file group 3 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| QUANTUM_DOMAIN_REPORT.md | Duplicate file group 4 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/QUANTUM_DOMAIN_REPORT.md | Duplicate file group 4 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| QUANTUM_FITNESS_REPORT.md | Duplicate file group 5 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/QUANTUM_FITNESS_REPORT.md | Duplicate file group 5 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| QUANTUM_KNOWLEDGE_REPORT.md | Duplicate file group 6 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/QUANTUM_KNOWLEDGE_REPORT.md | Duplicate file group 6 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| QUANTUM_SANDBOX_REPORT.md | Duplicate file group 7 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/QUANTUM_SANDBOX_REPORT.md | Duplicate file group 7 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| run_all_benchmarks.py | Duplicate file group 8 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/run_all_benchmarks.py | Duplicate file group 8 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| synergy_registry.json | Duplicate file group 9 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| physics/artifacts/domain_adaptation_results.json | Duplicate file group 9 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| artifacts/sota_results.csv | Duplicate file group 10 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| results/phase8c/sota_benchmark.csv | Duplicate file group 10 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/.gitignore | Duplicate file group 11 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/.gitignore | Duplicate file group 11 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/AGENTS.md | Duplicate file group 12 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/AGENTS.md | Duplicate file group 12 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/CLAUDE.md | Duplicate file group 13 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/CLAUDE.md | Duplicate file group 13 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/next-env.d.ts | Duplicate file group 14 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/next-env.d.ts | Duplicate file group 14 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| physics/benchmark_log.txt | Duplicate file group 15 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| physics/agents/__init__.py | Duplicate file group 15 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| physics/core/__init__.py | Duplicate file group 15 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| physics/unification_search/__init__.py | Duplicate file group 15 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| physics/warp/__init__.py | Duplicate file group 15 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/satellite/warp/__init__.py | Duplicate file group 15 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/next.config.ts | Duplicate file group 20 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/next.config.ts | Duplicate file group 20 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/package-lock.json | Duplicate file group 21 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/package-lock.json | Duplicate file group 21 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/package.json | Duplicate file group 22 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/package.json | Duplicate file group 22 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/playwright.config.ts | Duplicate file group 23 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/playwright.config.ts | Duplicate file group 23 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/postcss.config.mjs | Duplicate file group 24 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/postcss.config.mjs | Duplicate file group 24 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/tsconfig.json | Duplicate file group 25 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/tsconfig.json | Duplicate file group 25 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE3_HARDWARE_AWARE_REPORT.md | Duplicate file group 26 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE3_HARDWARE_AWARE_REPORT.md | Duplicate file group 26 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE3_HARDWARE_AWARE_RESULTS.csv | Duplicate file group 27 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/COMPLETE_PHASE3_RESULTS.csv | Duplicate file group 27 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE3_HARDWARE_AWARE_RESULTS.csv | Duplicate file group 27 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE3_INVESTOR_SUMMARY.md | Duplicate file group 28 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/investor_executive_summary.md | Duplicate file group 28 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE3_INVESTOR_SUMMARY.md | Duplicate file group 28 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE4_COMMERCIAL_POSITIONING.md | Duplicate file group 29 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE4_COMMERCIAL_POSITIONING.md | Duplicate file group 29 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE4_COMPETITIVE_ADVANTAGE_REPORT.md | Duplicate file group 30 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE4_COMPETITIVE_ADVANTAGE_REPORT.md | Duplicate file group 30 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE4_INVESTOR_SUMMARY.md | Duplicate file group 31 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE4_INVESTOR_SUMMARY.md | Duplicate file group 31 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE4_WORKLOAD_ANALYSIS.csv | Duplicate file group 32 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE4_WORKLOAD_ANALYSIS.csv | Duplicate file group 32 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE5_GENERALIZATION_RESULTS.csv | Duplicate file group 33 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE5_GENERALIZATION_RESULTS.csv | Duplicate file group 33 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE5_INVESTOR_SUMMARY.md | Duplicate file group 34 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE5_INVESTOR_SUMMARY.md | Duplicate file group 34 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE5_IP_REPORT.md | Duplicate file group 35 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE5_IP_REPORT.md | Duplicate file group 35 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE5_MOTIF_DATABASE.csv | Duplicate file group 36 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE5_MOTIF_DATABASE.csv | Duplicate file group 36 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/QADE_MOTIF_DATABASE.csv | Duplicate file group 36 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE5_MOTIF_DATABASE.json | Duplicate file group 37 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE5_MOTIF_DATABASE.json | Duplicate file group 37 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/QADE_MOTIF_DATABASE.json | Duplicate file group 37 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE5_TOP_MOTIFS.csv | Duplicate file group 38 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE5_TOP_MOTIFS.csv | Duplicate file group 38 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE6_COMPETITIVE_MOAT_REPORT.md | Duplicate file group 39 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE6_COMPETITIVE_MOAT_REPORT.md | Duplicate file group 39 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE6_ECONOMIC_IMPACT_REPORT.md | Duplicate file group 40 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE6_ECONOMIC_IMPACT_REPORT.md | Duplicate file group 40 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE6_INVESTOR_SUMMARY.md | Duplicate file group 41 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE6_INVESTOR_SUMMARY.md | Duplicate file group 41 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE6_IP_PORTFOLIO_VALUE.csv | Duplicate file group 42 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE6_IP_PORTFOLIO_VALUE.csv | Duplicate file group 42 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE6_IP_VALUATION_REPORT.md | Duplicate file group 43 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE6_IP_VALUATION_REPORT.md | Duplicate file group 43 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE6_LICENSING_MODEL.md | Duplicate file group 44 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE6_LICENSING_MODEL.md | Duplicate file group 44 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE6_MOTIF_ECONOMICS.csv | Duplicate file group 45 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE6_MOTIF_ECONOMICS.csv | Duplicate file group 45 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE6_RISK_ANALYSIS.md | Duplicate file group 46 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE6_RISK_ANALYSIS.md | Duplicate file group 46 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE6_WORKLOAD_ECONOMICS.csv | Duplicate file group 47 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE6_WORKLOAD_ECONOMICS.csv | Duplicate file group 47 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_COMPETITIVE_GAP.csv | Duplicate file group 48 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE7_COMPETITIVE_GAP.csv | Duplicate file group 48 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_COMPETITIVE_GAP_REPORT.md | Duplicate file group 49 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE7_COMPETITIVE_GAP_REPORT.md | Duplicate file group 49 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_ECONOMIC_MOAT_REPORT.md | Duplicate file group 50 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE7_ECONOMIC_MOAT_REPORT.md | Duplicate file group 50 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_EXECUTIVE_SUMMARY.md | Duplicate file group 51 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE7_EXECUTIVE_SUMMARY.md | Duplicate file group 51 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_INVESTOR_POSITIONING.md | Duplicate file group 52 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE7_INVESTOR_POSITIONING.md | Duplicate file group 52 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_KNOWLEDGE_FLYWHEEL_REPORT.md | Duplicate file group 53 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE7_KNOWLEDGE_FLYWHEEL_REPORT.md | Duplicate file group 53 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_KNOWLEDGE_GROWTH.csv | Duplicate file group 54 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE7_KNOWLEDGE_GROWTH.csv | Duplicate file group 54 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_MOAT_SCORES.csv | Duplicate file group 55 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE7_MOAT_SCORES.csv | Duplicate file group 55 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_NETWORK_EFFECT.csv | Duplicate file group 56 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/results/PHASE7_NETWORK_EFFECT.csv | Duplicate file group 56 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_NETWORK_EFFECT_REPORT.md | Duplicate file group 57 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE7_NETWORK_EFFECT_REPORT.md | Duplicate file group 57 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/PHASE7_PLATFORM_ANALYSIS.md | Duplicate file group 58 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| benchmarks/reports/PHASE7_PLATFORM_ANALYSIS.md | Duplicate file group 58 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/REPRODUCIBILITY_30_SEED_FINAL_REPORT.md | Duplicate file group 59 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| docs/REPRODUCIBILITY_IMPROVED_30_SEED_FINAL_REPORT.md | Duplicate file group 59 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| physics/__init__.py | Duplicate file group 60 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/physics/__init__.py | Duplicate file group 60 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/black_compliance_report.md | Duplicate file group 61 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/VERIFICATION_BASELINE_v4/black_compliance_report.md | Duplicate file group 61 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/cdr_final_review_board_report.md | Duplicate file group 62 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/VERIFICATION_BASELINE_v4/cdr_final_review_board_report.md | Duplicate file group 62 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/CDR_READINESS_REVIEW.md | Duplicate file group 63 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/coverage_summary.json | Duplicate file group 64 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/coverage_summary_v4_candidate.json | Duplicate file group 65 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/VERIFICATION_BASELINE_v4/coverage_summary.json | Duplicate file group 65 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/ekf_validation_report.md | Duplicate file group 66 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/VERIFICATION_BASELINE_v4/ekf_validation_report.md | Duplicate file group 66 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/flight_heritage_calibration_report.md | Duplicate file group 67 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/VERIFICATION_BASELINE_v4/flight_heritage_calibration_report.md | Duplicate file group 67 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/flight_heritage_calibration_results.csv | Duplicate file group 68 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/VERIFICATION_BASELINE_v4/flight_heritage_calibration_results.csv | Duplicate file group 68 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/VERIFICATION_BASELINE_v4/heritage_comparison.csv | Duplicate file group 68 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/satellite/validation/heritage_comparison.csv | Duplicate file group 68 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/geometry_pareto_front.csv | Duplicate file group 69 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/datasets/geometry_pareto_front.csv | Duplicate file group 69 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/hil_results.csv | Duplicate file group 70 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/datasets/hil_results.csv | Duplicate file group 70 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/satellite/thermal/hil_results.csv | Duplicate file group 70 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/pydantic_migration_report.md | Duplicate file group 71 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/VERIFICATION_BASELINE_v4/pydantic_migration_report.md | Duplicate file group 71 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/verification_dashboard.csv | Duplicate file group 72 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/e2e/scientificQA.spec.ts | Duplicate file group 74 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/e2e/scientificQA.spec.ts | Duplicate file group 74 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/public/file.svg | Duplicate file group 75 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/public/file.svg | Duplicate file group 75 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/public/globe.svg | Duplicate file group 76 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/public/globe.svg | Duplicate file group 76 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/public/next.svg | Duplicate file group 77 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/public/next.svg | Duplicate file group 77 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/public/vercel.svg | Duplicate file group 78 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/public/vercel.svg | Duplicate file group 78 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| dashboard/public/window.svg | Duplicate file group 79 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
| satelite/dashboard/public/window.svg | Duplicate file group 79 | Medium | REVIEW | Canonical duplicate group owner | REVIEW |
