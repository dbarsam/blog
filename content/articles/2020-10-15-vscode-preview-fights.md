---
title: VSCode's Word Wrap vs. Preview Sync
date: 2020-10-15 09:15
tags: vscode
slug: vscode-editor-preview-sync
authors: db
summary: VSCode's preview synchronization is a nice feature -- when it works...
header_cover: /images/article-bg.png
status: published
categories: developer set-up
category: developer set-up
type: article
---

VSCode has a nice preview engine that allows a side-by-side of text and rendered-text. The feature is best documented in VSCode's native [Markdown] support help, but it's available for other languages and their plugins.

Within that help page is the section on [Editor and Preview Synchronization].  This is a nice feature but suffers from a locked up, sync-cycle battle between the editor pane and preview pane that leaves the user frustrated and fighting for control of the editor.

The fun starts when there's a big discrepancy between the screen space  taken by the text editor's monospace text and the previewer's html-looking rendered text.  There are various ways to make this happen, but the one way that seems to be consistent, is to enable the preview and word wrapping at the same time.

When both options are enabled, the synchronization seems to struggle with the concept of word wrap; after the cursor goes 'below the fold' of the bottom terminal panels, the sync (for some reason) decides to scroll the editor back to top of the file.  But because you're in the middle of typing, the editor then immediately jumps back down to bottom, where the cursor is.  Of course, the synchronization is still active, so the editor jumps back up to the top and the cycle repeats for every keyboard click.

![vscode-editor-preview-sync.gif]

This is seems like the same issue described in Visual Code issues #[108582], but the comments suggest that people are still suffering from it.  Until it's properly fixed, the best answer is to disable that feature by setting the `markdown.preview.scrollEditorWithPreview` setting to `false`:

```json
{
    ....
    "markdown.preview.scrollEditorWithPreview": false,
    ....
}

```

[Markdown]: https://code.visualstudio.com/Docs/languages/markdown
[Editor and Preview Synchronization]: https://code.visualstudio.com/Docs/languages/markdown#_editor-and-preview-synchronization
[108582]: https://github.com/microsoft/vscode/issues/108582
[vscode-editor-preview-sync.gif]: ..\images\articles\2020-10-15-vscode-preview-fights\vscode-example.gif
