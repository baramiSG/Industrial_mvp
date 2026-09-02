# v0.2.0 documentary browser references

**DOCUMENTARY REFERENCE ONLY — NOT A VISUAL-REGRESSION ORACLE.**

No test compares these images. Governed visual-regression baselines begin in S07 under owner ruling R-4.

## Provenance

- Product release: `v0.2.0` (`ce5786b423f2b5de81e13a73c1fbe57da2a8f5e6`)
- S06 base commit: `d338f5d9ed49457d3a595b2d1e6b4f0bb7683efc`
- Playwright package: `1.62.0`
- pytest-playwright package: `0.9.0`
- Chromium: `151.0.7922.34`
- Arabic fontconfig match: `DejaVu Sans` (`/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`)
- Capture command: `E2E_REFERENCE_DIR=.workflow/slices/S06-browser-acceptance-harness/reference-screenshots/v0.2.0 make e2e`
- Format: WebP quality 55; scoped element captures
- Matrix: 40 files; 4650022 aggregate bytes

## Captured UI source hashes

- `src/ior_mvp/static/index.html`: `031a50038d3fd2ff7c1113644e8774645ec508e741941b4fc166d847c7298398`
- `src/ior_mvp/static/app.js`: `ade715f162099353b51aa6958085c310216988f461c5c386adfbd419635d312f`
- `src/ior_mvp/static/styles.css`: `d9e1843c48d5fc338fa0f335a41854beefe6a8dda42f6bd0e1d0d73fa78030b7`
- `src/ior_mvp/dossier.py`: `24d8ff3f5462fd56c3b54be449ee62c0a9a794cb25f216663483bcd14a48f470`

## Journey matrix

| Viewport | Journey state | Mode | Case | Real state | Active state | File | Bytes | SHA-256 |
|---|---|---|---|---|---|---|---:|---|
| desktop-1440x900 (1440×900) | A: journey-a-portfolio-public | public | portfolio | steel=INVESTIGATE; polypropylene=REJECT | steel=INVESTIGATE; polypropylene=REJECT | `desktop-1440x900__journey-a-portfolio-public.webp` | 39432 | `f8ac4c42b7329b66f9d3ba4826294d82c1f9172b6c411b4f70e4bf6e33779214` |
| desktop-1440x900 (1440×900) | A: journey-a-portfolio-simulated | simulated | portfolio | steel=INVESTIGATE; polypropylene=REJECT | steel=ADVANCE; polypropylene=REJECT | `desktop-1440x900__journey-a-portfolio-simulated.webp` | 39558 | `e8f1ade880ed0b24cd7075c03fa1dac6d03750634f78cec424bf35e139d340dc` |
| desktop-1440x900 (1440×900) | B: journey-b-steel-public-workspace | public | SAU-H0-721049 | INVESTIGATE | INVESTIGATE | `desktop-1440x900__journey-b-steel-public-workspace.webp` | 175518 | `6cb7b71b56ee569c7bcad9e8dd4acb99608a9b4325e1db45fd26144df63cfd1a` |
| desktop-1440x900 (1440×900) | C: journey-c-steel-simulated-workspace | simulated | SAU-H0-721049 | INVESTIGATE | ADVANCE | `desktop-1440x900__journey-c-steel-simulated-workspace.webp` | 230984 | `0ebd128f3e078789a76b26091f46414142a7469fb7bf783f415cd5096e2ffc54` |
| desktop-1440x900 (1440×900) | D: journey-d-polypropylene-public-workspace | public | SAU-H0-390210 | REJECT | REJECT | `desktop-1440x900__journey-d-polypropylene-public-workspace.webp` | 159776 | `5625b87dbbef76aa44d94898ce33301d591b75724a03ebe9f1edf4f8eae6154b` |
| desktop-1440x900 (1440×900) | D: journey-d-polypropylene-simulated-workspace | simulated | SAU-H0-390210 | REJECT | REJECT | `desktop-1440x900__journey-d-polypropylene-simulated-workspace.webp` | 210054 | `87acfb6b8c21e3c34f290f8587042a4ba4eb00e3d65f43ec33a9a3f6a67ba48f` |
| desktop-1440x900 (1440×900) | E: journey-e-steel-public-dossier | public | SAU-H0-721049 | INVESTIGATE | INVESTIGATE | `desktop-1440x900__journey-e-steel-public-dossier.webp` | 64966 | `251a717ebcf365845f827990918b14bbba1cf54cc7244ce03494e7f0f7222385` |
| desktop-1440x900 (1440×900) | E: journey-e-steel-simulated-dossier | simulated | SAU-H0-721049 | INVESTIGATE | ADVANCE | `desktop-1440x900__journey-e-steel-simulated-dossier.webp` | 100168 | `5d6ff3dc9a3315b740ae8bea1d607cc70e3adfe0d6f89d652db0d661f27db13d` |
| desktop-1440x900 (1440×900) | E: journey-e-polypropylene-public-dossier | public | SAU-H0-390210 | REJECT | REJECT | `desktop-1440x900__journey-e-polypropylene-public-dossier.webp` | 48894 | `a6c4a0494bba0913af2dba0d258326ab29cb3b229b08be07a3239f35a12e8884` |
| desktop-1440x900 (1440×900) | E: journey-e-polypropylene-simulated-dossier | simulated | SAU-H0-390210 | REJECT | REJECT | `desktop-1440x900__journey-e-polypropylene-simulated-dossier.webp` | 78746 | `bd3501f2f23592b017d80b1e9c9346c586755ab81350bd4c8f2d0558970ce557` |
| tablet-1024x768 (1024×768) | A: journey-a-portfolio-public | public | portfolio | steel=INVESTIGATE; polypropylene=REJECT | steel=INVESTIGATE; polypropylene=REJECT | `tablet-1024x768__journey-a-portfolio-public.webp` | 39082 | `21fd830e2d75fe2b58e841d5000df825408be956db99c0b3603d09586d9f4d11` |
| tablet-1024x768 (1024×768) | A: journey-a-portfolio-simulated | simulated | portfolio | steel=INVESTIGATE; polypropylene=REJECT | steel=ADVANCE; polypropylene=REJECT | `tablet-1024x768__journey-a-portfolio-simulated.webp` | 39212 | `e488f00e299cb79275c5c8d23ac910fec295c6884e437411c146a201911346c0` |
| tablet-1024x768 (1024×768) | B: journey-b-steel-public-workspace | public | SAU-H0-721049 | INVESTIGATE | INVESTIGATE | `tablet-1024x768__journey-b-steel-public-workspace.webp` | 164586 | `55568669cbf2ae11b35178b2a084de5da1e6803ad143a68a78814accc229b767` |
| tablet-1024x768 (1024×768) | C: journey-c-steel-simulated-workspace | simulated | SAU-H0-721049 | INVESTIGATE | ADVANCE | `tablet-1024x768__journey-c-steel-simulated-workspace.webp` | 223530 | `71a6ad2ba6bfcd2752cbd3189d99b6b556d55f69be3db2c355cd2b9e380753fe` |
| tablet-1024x768 (1024×768) | D: journey-d-polypropylene-public-workspace | public | SAU-H0-390210 | REJECT | REJECT | `tablet-1024x768__journey-d-polypropylene-public-workspace.webp` | 153508 | `8932a8528ee5a4044785ecc78a16b6f878ead0c0d270cd927162b4f49bd6400c` |
| tablet-1024x768 (1024×768) | D: journey-d-polypropylene-simulated-workspace | simulated | SAU-H0-390210 | REJECT | REJECT | `tablet-1024x768__journey-d-polypropylene-simulated-workspace.webp` | 205142 | `7f7363e7a6d555dff354f91a5f0913079d2cc079265680147e1928f196ee0716` |
| tablet-1024x768 (1024×768) | E: journey-e-steel-public-dossier | public | SAU-H0-721049 | INVESTIGATE | INVESTIGATE | `tablet-1024x768__journey-e-steel-public-dossier.webp` | 64556 | `f4bf4848ae34f005960667bc71e22e2e0535dc62157d891e1351de1ea39bbec7` |
| tablet-1024x768 (1024×768) | E: journey-e-steel-simulated-dossier | simulated | SAU-H0-721049 | INVESTIGATE | ADVANCE | `tablet-1024x768__journey-e-steel-simulated-dossier.webp` | 100616 | `0c0283876d85f9cb84096f7dde6eabe83b3178b14537efd3f7fcff69c6225d00` |
| tablet-1024x768 (1024×768) | E: journey-e-polypropylene-public-dossier | public | SAU-H0-390210 | REJECT | REJECT | `tablet-1024x768__journey-e-polypropylene-public-dossier.webp` | 49422 | `bd87f6b0a99adab48de7ecf825348c65b4cb6e1912b53f4c4a6fc41eb23dac26` |
| tablet-1024x768 (1024×768) | E: journey-e-polypropylene-simulated-dossier | simulated | SAU-H0-390210 | REJECT | REJECT | `tablet-1024x768__journey-e-polypropylene-simulated-dossier.webp` | 79908 | `b4e79b7e339dac944b6e20d7bfb61ee13f972d1c2a84d615b4699b0d70f816b2` |
| presentation-1920x1080 (1920×1080) | A: journey-a-portfolio-public | public | portfolio | steel=INVESTIGATE; polypropylene=REJECT | steel=INVESTIGATE; polypropylene=REJECT | `presentation-1920x1080__journey-a-portfolio-public.webp` | 39718 | `9616abdf8319a710fe9ffa287a51694040ad8a9d7e079f3ff01fb7faf6681c7c` |
| presentation-1920x1080 (1920×1080) | A: journey-a-portfolio-simulated | simulated | portfolio | steel=INVESTIGATE; polypropylene=REJECT | steel=ADVANCE; polypropylene=REJECT | `presentation-1920x1080__journey-a-portfolio-simulated.webp` | 39820 | `4405881f501c76bcb1bdd7cd1c956b1674207d6e9ad2576300a91e4b05534c55` |
| presentation-1920x1080 (1920×1080) | B: journey-b-steel-public-workspace | public | SAU-H0-721049 | INVESTIGATE | INVESTIGATE | `presentation-1920x1080__journey-b-steel-public-workspace.webp` | 180780 | `578add5f967ae77b1409f2e98c77e3b9df843b768f68ac3e77ba2293d98719bd` |
| presentation-1920x1080 (1920×1080) | C: journey-c-steel-simulated-workspace | simulated | SAU-H0-721049 | INVESTIGATE | ADVANCE | `presentation-1920x1080__journey-c-steel-simulated-workspace.webp` | 236782 | `ac69213d222a904c4727616174f05cb17a683e31b662a1e50cfc6df86decc5bf` |
| presentation-1920x1080 (1920×1080) | D: journey-d-polypropylene-public-workspace | public | SAU-H0-390210 | REJECT | REJECT | `presentation-1920x1080__journey-d-polypropylene-public-workspace.webp` | 164038 | `f0a5e6920c292be1ef45a9d91679d28e5b76e9d8f54b2a2c65cc730cf9ba5a82` |
| presentation-1920x1080 (1920×1080) | D: journey-d-polypropylene-simulated-workspace | simulated | SAU-H0-390210 | REJECT | REJECT | `presentation-1920x1080__journey-d-polypropylene-simulated-workspace.webp` | 216194 | `0589a969ace10dd635303cc4895f96e9cc42dc6ee54af7172b6977f458617ae2` |
| presentation-1920x1080 (1920×1080) | E: journey-e-steel-public-dossier | public | SAU-H0-721049 | INVESTIGATE | INVESTIGATE | `presentation-1920x1080__journey-e-steel-public-dossier.webp` | 64966 | `251a717ebcf365845f827990918b14bbba1cf54cc7244ce03494e7f0f7222385` |
| presentation-1920x1080 (1920×1080) | E: journey-e-steel-simulated-dossier | simulated | SAU-H0-721049 | INVESTIGATE | ADVANCE | `presentation-1920x1080__journey-e-steel-simulated-dossier.webp` | 100168 | `5d6ff3dc9a3315b740ae8bea1d607cc70e3adfe0d6f89d652db0d661f27db13d` |
| presentation-1920x1080 (1920×1080) | E: journey-e-polypropylene-public-dossier | public | SAU-H0-390210 | REJECT | REJECT | `presentation-1920x1080__journey-e-polypropylene-public-dossier.webp` | 48904 | `2b2c8bf705316125da6ea5989f25257b3f00c180467026ef8285a3fe44aa3937` |
| presentation-1920x1080 (1920×1080) | E: journey-e-polypropylene-simulated-dossier | simulated | SAU-H0-390210 | REJECT | REJECT | `presentation-1920x1080__journey-e-polypropylene-simulated-dossier.webp` | 78736 | `769bb7626796a0ade03379c2a16f6c46ed8da50f49bb17b08e1c2b8d30a5e937` |
| presentation-2560x1440 (2560×1440) | A: journey-a-portfolio-public | public | portfolio | steel=INVESTIGATE; polypropylene=REJECT | steel=INVESTIGATE; polypropylene=REJECT | `presentation-2560x1440__journey-a-portfolio-public.webp` | 40534 | `946bc52c7de28780b6c259712550d29051106a575399fc2912b004aaf440163d` |
| presentation-2560x1440 (2560×1440) | A: journey-a-portfolio-simulated | simulated | portfolio | steel=INVESTIGATE; polypropylene=REJECT | steel=ADVANCE; polypropylene=REJECT | `presentation-2560x1440__journey-a-portfolio-simulated.webp` | 40688 | `13fa3e111743202edc72faf649875b8fb7bd9b77dc19b8239522618537d7672e` |
| presentation-2560x1440 (2560×1440) | B: journey-b-steel-public-workspace | public | SAU-H0-721049 | INVESTIGATE | INVESTIGATE | `presentation-2560x1440__journey-b-steel-public-workspace.webp` | 190326 | `ff504e58fc80e5b47fe346a8643118b3c0756a9582b6911d76c658a410e64c83` |
| presentation-2560x1440 (2560×1440) | C: journey-c-steel-simulated-workspace | simulated | SAU-H0-721049 | INVESTIGATE | ADVANCE | `presentation-2560x1440__journey-c-steel-simulated-workspace.webp` | 245674 | `5b44d6b9dc10d53b1b74db6a3ec6ca02b20375398be60b8bb18f3f6d25056c92` |
| presentation-2560x1440 (2560×1440) | D: journey-d-polypropylene-public-workspace | public | SAU-H0-390210 | REJECT | REJECT | `presentation-2560x1440__journey-d-polypropylene-public-workspace.webp` | 175884 | `29ef8cd9f00260bfa8946abdca2ffc333fb7bdcd44ce7044d3f221f77adec765` |
| presentation-2560x1440 (2560×1440) | D: journey-d-polypropylene-simulated-workspace | simulated | SAU-H0-390210 | REJECT | REJECT | `presentation-2560x1440__journey-d-polypropylene-simulated-workspace.webp` | 226408 | `2a8d91e13a996521b9df2244d3a6f7f5d058ee2f4226e1a87e5cc52f592c825c` |
| presentation-2560x1440 (2560×1440) | E: journey-e-steel-public-dossier | public | SAU-H0-721049 | INVESTIGATE | INVESTIGATE | `presentation-2560x1440__journey-e-steel-public-dossier.webp` | 64984 | `a3d3e0b40ff6dd2c68477cf7290bb27f2895289b8b2607427f3de4ef41359617` |
| presentation-2560x1440 (2560×1440) | E: journey-e-steel-simulated-dossier | simulated | SAU-H0-721049 | INVESTIGATE | ADVANCE | `presentation-2560x1440__journey-e-steel-simulated-dossier.webp` | 100186 | `023edb44a00365458e973c7fed59407de75c064557281996093fdaa9a8d70fc1` |
| presentation-2560x1440 (2560×1440) | E: journey-e-polypropylene-public-dossier | public | SAU-H0-390210 | REJECT | REJECT | `presentation-2560x1440__journey-e-polypropylene-public-dossier.webp` | 48896 | `6425b15db1ad3582d805102e39c1816bc6b3778432a3fbead72246795df7552a` |
| presentation-2560x1440 (2560×1440) | E: journey-e-polypropylene-simulated-dossier | simulated | SAU-H0-390210 | REJECT | REJECT | `presentation-2560x1440__journey-e-polypropylene-simulated-dossier.webp` | 78678 | `fb6960fdeba340f25e387156305860b06cb120c1a307080f673659c0d921ba90` |
