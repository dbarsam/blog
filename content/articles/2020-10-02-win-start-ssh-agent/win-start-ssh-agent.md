---
title: The problem with start-ssh-agent.cmd
date: 2020-10-02 09:44
tags: ssh, git, cmd
slug: start-ssh-agent
authors: db
summary: There's a small bit of inconvenience in Git's convenience script.
header_cover: /images/article-bg.png
status: published
categories: developer set-up
category: developer set-up
type: article
---
<!--
spell-checker:ignore
-->
When you install Git on Windows, the installer will also install the utility script `start-ssh-agent.cmd`.  That script isn't necessarily required to use Git, but if you fall into a narrow category of users who have a particular workflow, you can get tripped up by one of its unfortunate side effects.

## SSH, Not HTTP

That workflow starts with command-line Git and 2FA.  2FA is a pretty much the standard security feature for any online service.  Most of the time the 2FA is handled by a web site with a nice UI, but working with it on the Windows command line requires a bit more work.

Git already provides an authentication layer for connecting to remote repositories.  This is usually a choice between SSH keys or a HTTP username/password prompt.  While SSH is more secure than HTTP, HTTP is easier to understand and requires no set-up.  However, with 2FA enabled, the ease-of-use goes away as 2FA adds an extra handling on top of the HTTP process.  SHH, on the other hand, doesn't required that extra handling as it's already providing the same level of security.  So in the end it's simpler to work with SSH keys -- but SSH security really isn't as easily presentable to the Windows user as it is in Unix system.

## CMD, Not Git Bash

After selecting SSH, the next part of the workflow is choosing to use SSH with the Windows command line, aka `cmd.exe`.  The challenge there is that `cmd.exe` doesn't provide the same functionality that Unix shells do.  Most of the available tutorials that deal Git on Windows will usually use a Git Bash shell because it's bundle with Git and has the same experience as the existing Unix tutorials.

For example, let's assume that you create a GitHub SSH key using the [GitHub docs] and add it to your `.ssh` folder.  SSH requires an agent running in the background to handle a persistent connection.  On Bash it's started with the ``eval `ssh-agent` `` command.  The `ssh-agent` function returns a collection of environment variables needed by other processes to use the agent:

```console
db@PC-5559 MINGW64 ~
$ ssh-agent
SSH_AUTH_SOCK=/tmp/ssh-nubDqpgoGDRA/agent.4548; export SSH_AUTH_SOCK;
SSH_AGENT_PID=18568; export SSH_AGENT_PID;
echo Agent pid 18568;
```

Wrapping this up with the `eval` command simply executes that output text as shell script and sets the environment variables.

 There's no equivalent of that in Windows.  Instead, you can use the `start-ssh-agent.cmd` script, which is usually installed in `C:\Program Files\Git\cmd` and added to the Window's `PATH` by the Git installer.  The `start-ssh-agent.cmd` is a bit more complex but accomplishes the same thing -- except for a little bit of shenanigans at the end of the script.

## Windows Explorer vs cmd.exe

The problem with the script is that it misses the mark when it makes a guess about the user's intention.  The script looks at the `%cmdcmdline%` environment variable and re-executes the script in a nested call depending on the contents.

```cmd
@ECHO %cmdcmdline% | @FINDSTR /l "\"\"" >NUL
@IF NOT ERRORLEVEL 1 @(
    @CALL cmd %*
)
```

The variable contains the command line arguments used to launch the `cmd.exe` process.  When the script is launched from the command line, it contains `"C:\Windows\system32\cmd.exe"`, but when the script is executed from a double click in Windows Explorer, that value is `C:\WINDOWS\system32\cmd.exe /c ""C:\Program Files\Git\cmd\start-ssh-agent.cmd" "`.  When the `start-ssh-cmd.exe` sees the `""` it will launch an interactive child session to keep the command prompt open.

By itself this isn't really isn't a problem. If the check wasn't there, then the session would naturally terminate as soon as the script ended.  This is useless because any ssh environment variables created would have been local to that short-lived session.

## Session Managers

The problem comes in the last stage of the workflow, where you're using a customized Windows shell tool, like with [cmder] or [ConeEmu].  Both tools provide a way to customize and manage multiple shell sessions, which is useful when you need to juggle shells like [Visual Studio developer shell] or [Anaconda] in a tab manager.

If you want to add `start-ssh-agent.cmd` to one of those shells, you'll need to pay close attention to the tool's start script.  If it contain the same `""` pattern, it will spawn a new, nested session within the original session as it was launched from Windows Explorer.  It won't be readily apparent, but the quickest way to identify this new symptom is if exiting the shell somehow requires two `exit` commands.

The work around (from this [post]) is to supply the `/k exit` args to immediately kill the nested session:

```cmd
call "%GIT_INSTALL_ROOT%\cmd\start-ssh-agent.cmd" /k exit
```

The `/k exit` will be passed through to the nested session and quick exit it, leaving the original parent session that your session manager is managing.

[post]: https://github.com/cmderdev/cmder/issues/1807#issuecomment-400504725
[cmder]: https://cmder.net
[ConeEmu]: https://conemu.github.io
[GitHub docs]: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
[visual studio Developer shell]: https://docs.microsoft.com/en-us/visualstudio/ide/reference/command-prompt-powershell?view=vs-2019
[anaconda]: https://docs.anaconda.com/ae-notebooks/user-guide/basic-tasks/apps/use-terminal/
