Rust -  Shell like Process pipelines using subprocess crate
###########################################################

:date: 2017-06-18 20:59 +0530
:slug: shell-pipelines-rust
:tags: rust, subprocess
:author: copyninja
:summary: Post briefly describes running shell command pipelines in Rust using
          subprocess crate.

I had to extract copyright information from the git repository of the crate
upstream. The need aroused as part of updating *debcargo*, tool to create Debian
package source from the Rust crate.

General idea behind taking copyright information from git is to extract starting
and latest contribution year for every author/committer. This can be easily
achieved using following shell snippet

.. code-block:: shell

   for author in $(git log --format="%an" | sort -u); do
      author_email=$(git log --format="%an <%ae>" --author="$author" | head -n1)
      first=$(git \
      log --author="$author" --date=format:%Y --format="%ad" --reverse \
                | head -n1)
      latest=$(git log --author="$author" --date=format:%Y --format="%ad" \
                | head -n1)
      if [ $first -eq $latest ]; then
          echo "$first, $author_email"
      else
          echo "$first-$latest, $author_email"
      fi
   done

Now challenge was to execute these command in Rust and get the required answer.
So first step was I looked at *std::process*, default standard library support
for executing shell commands.

My idea was to execute first command to extract authors into a Rust *vectors* or
*array* and then have 2 remaining command to extract years in a loop. (Yes I do
not need additional author_email command in Rust as I can easily get both in the
first command which is used in for loop of shell snippet and use it inside
another loop). So I setup to 3 commands outside the loop with input and output
redirected, following is snippet should give you some idea of what I tried to do.

.. code-block:: rust

   let authors_command = Command::new("/usr/bin/git")
                .arg("log")
                .arg("--format=\"%an <%ae>\"")
                .spawn()?;
   let output = authors_command.wait()?;
   let authors: Vec<String> = String::from_utf8(output.stdout).split('\n').collect();
   let head_n1 = Command::new("/usr/bin/head")
                .arg("-n1")
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .spwn()?;
   for author in &authors {
                ...
   }


And inside the loop I would create additional 2 git commands read their output
via pipe and feed it to head command. This is where I learned that it is not
straight forward as it looks :-). *std::process::Command* type does not
implement *Copy* nor *Clone* traits which means one use of it I will give up the
ownership!. And here I started fighting with borrow checker. I need to duplicate
declarations to make sure I've required commands available all the time.
Additionally I needed to handle error output at every point which created too
many nested statements there by complicating the program and reducing its
readability

When all started getting out of control I gave a second thought and wondered if
it would be good to write down this in shell script ship it along with debcargo
and use the script Rust program. This would satisfy my need but I would need to
ship additional script along with debcargo which I was not really happy with.

Then a search on crates.io revealed *subprocess*, a crate designed to be similar
with *subprocess* module from Python!. Though crate is not highly downloaded it
still looked promising, especially the trait implements a trait called `BitOr`
which allows use of `|` operator to chain the commands. Additionally it allows
executing full shell commands without need of additional chaining of argument
which was done above snippet. End result a much simplified easy to read and
correct function which does what was needed. Below is the function I wrote to
extract copyright information from git repo.

.. code-block:: rust

   fn copyright_fromgit(repo: &str) -> Result<Vec<String>> {
       let tempdir = TempDir::new_in(".", "debcargo")?;
       Exec::shell(OsStr::new(format!("git clone --bare {} {}",
                                   repo,
                                   tempdir.path().to_str().unwrap())
                                 .as_str())).stdout(subprocess::NullFile)
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
           let reverse_command = format!("git log --author=\"{}\" --format=%ad --date=format:%Y \
                                       --reverse",
                                      author);
           let command = format!("git log --author=\"{}\" --format=%ad --date=format:%Y",
                              author);
           let first = {
                Exec::shell(OsStr::new(&reverse_command)).cwd(tempdir.path()) |
                Exec::shell(OsStr::new("head -n1"))
            }.capture()?;

            let latest = {
                Exec::shell(OsStr::new(&command)).cwd(tempdir.path()) | Exec::shell("head -n1")
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

Of course it is not as short as the shell or probably Python code, but that is
fine as Rust is system level programming language (which is intended to replace
C/C++) and doing complex Shell code (complex due to need of shell pipelines) in
approximately 50 lines of code in safe and secure way is very much acceptable.
Besides code is as much readable as a plain shell snippet thanks to the `|`
operator implemented by subprocess crate.
