---
name: objekt-drawings-go-to-drive
description: Every drawing set I make for an objekt product must also be uploaded to that product's Drive design folder
metadata:
  type: feedback
---

Sabry said (1 Nov 2026): add the drawings I make into the product folder. After producing a drawing PDF and production pack, upload both to the product's folder under "OBJEKT design files" in Drive. OBJ-002 (rev5), OBJ-038 (rev4), OBJ-015 (rev1) and OBJ-169 (rev0, stamped approved) are uploaded.

**Why:** Production works from the Drive folders linked in the book and workspace, not from my local files.
**How to apply:** Chrome hidden-input + one synthetic drop; steps are step 11 of the objekt-drawings skill. Look in the folder first; a second drop triggers a replace dialog, cancel it. See [[objekt-drawings-standard]].

**Production book sticker (1 Nov 2026):** every product slide has a pill top-right, id `flag_NNN` (e.g. flag_166): green "DESIGN FILE READY" or yellow "DESIGN FILE NOT READY", plus a legend on the index slide. When a drawing set is approved and in Drive, turn that product's pill green (fill rgb 0.18,0.49,0.20, white text) and change the "Design file:" line in its text boxes. Green so far: OBJ-002, 012, 015 (rev 1, approved 1 Nov), 038, 152, 166, 167, 169 (rev 2, approved 2 Nov; rev 0 and rev 1 were wrong, the stand was misread). After flipping the fill, also set the pill text to white: replaceAllText keeps the old dark text colour.

**Approval slip (2 Nov 2026, OBJ-169):** my stamp patch asserted but the python after it still ran the old file, so I uploaded the DRAFT PDF as the asset. Check the PDF text for the approved stamp (not DRAFT) before any asset upload, and replace stamp lines by line number copied from an approved generator, not by escaped-string match.

**OBJ-169 stand lesson (2 Nov 2026):** I asked 'under the ridges or under the face mid-lines?' and Sabry said 'wym?' then approved without deciding; I drew the ridge option and it was wrong. When a drawing choice cannot be settled from the photo, zoom the photo to 4x first and decide from what it shows; do not ship an approved drawing with an open question that affects the geometry. Fix a wrong approved drawing immediately as a new revision, not by waiting for a better photo.
