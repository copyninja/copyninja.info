Update: - Shell pipelines with subprocess crate and use of Exec::shell function
###############################################################################

:date: 2017-06-19 20:48 +0530
:slug: update-shell-pipelines
:tags: rust, subprocess, shell inejctions
:author: copyninja
:summary: Update to my previous post on using Exec::shell from subprocess crates
          to create shell pipeline.

In my `previous post <https://copyninja.info/blog/shell-pipelines-rust.html>`_ I
used `Exec::shell` function from subprocess crate and passed it string generated
by interpolating *--author* argument. This string was then run by the shell via
`Exec::shell`. After publishing post I got ping on IRC by `Jonas Smedegaard
<https://wiki.debian.org/JonasSmedegaard>`_ and `Paul Wise
<https://wiki.debian.org/PaulWise>`_ that I should replace `Exec::shell`, as it
might be prone to errors or vulnerabilities of shell injection attack. Indeed
they were right, in hurry I did not completely read the function documentation
which clearly mentions this fact.

    When invoking this function, be careful not to interpolate arguments into
    the string run by the shell, such as Exec::shell(format!("sort {}",
    filename)). Such code is prone to errors and, if filename comes from an
    untrusted source, to shell injection attacks. Instead, use
    Exec::cmd("sort").arg(filename).

Though I'm not directly taking input from untrusted source, its still possible
that the string I got back from git log command might contain some oddly
formatted string with characters of different encoding which could possibly
break the `Exec::shell` , as I'm not sanitizing the shell command. When we use
`Exec::cmd` and pass argument using *.args* chaining, the library takes care of
creating safe command line. So I went in and modified the function to use
`Exec::cmd` instead of `Exec::shell`.

Below is updated function.

.. code-block:: rust

   fn copyright_fromgit(repo: &str) -> Result<Vec<String>> {
       let tempdir = TempDir::new_in(".", "debcargo")?;
       Exec::shell(OsStr::new(format!("git clone --bare {} {}",
                                   repo,
                                   tempdir.path().to_str().unwrap())
                               .as_str()))
        .stdout(subprocess::NullFile)
        .stderr(subprocess::NullFile)
        .popen()?;

       let author_process = {
           Exec::shell(OsStr::new("git log --format=\"%an <%ae>\"")).cwd(tempdir.path()) |
           Exec::shell(OsStr::new("sort -u"))
       }.capture()?;
       let authors = author_process.stdout_str().trim().to_string();
       let authors: Vec<&str> = authors.split('\n').collect();
       let mut notices: Vec<String> = Vec::new();
       for author in &authors {
           let author_string = format!("--author={}", author);
           let first = {
               Exec::cmd("/usr/bin/git")
                .args(&["log", "--format=%ad",
                       "--date=format:%Y",
                       "--reverse",
                       &author_string])
                .cwd(tempdir.path()) | Exec::shell(OsStr::new("head -n1"))
           }.capture()?;

           let latest = {
               Exec::cmd("/usr/bin/git")
                .args(&["log", "--format=%ad", "--date=format:%Y", &author_string])
                .cwd(tempdir.path()) | Exec::shell("head -n1")
           }.capture()?;

           let start = i32::from_str(first.stdout_str().trim())?;
           let end = i32::from_str(latest.stdout_str().trim())?;
           let cnotice = match start.cmp(&end) {
               Ordering::Equal => format!("{}, {}", start, author),
               _ => format!("{}-{}, {}", start, end, author),
           };

           notices.push(cnotice);
       }

       Ok(notices)
   }

I still use `Exec::shell` for generating author list, this is not problematic as
I'm not interpolating arguments to create command string.
