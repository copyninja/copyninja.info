debcargo: Replacing subprocess crate with git2 crate
####################################################

:date: 2017-07-15 15:35 +0530
:slug: using-git2-debcargo
:tags: rust, subprocess, git
:author: copyninja
:summary: Replace shell calls in debcargo to extract git information with git2
          library crate.

In my previous `post <https://copyninja.info/blog/shell-pipelines-rust.html>`_ I
talked about using *subprocess* crate to extract beginning and ending year from
git repository for generating debian/copyright file. In this post I'm going to
talk on how I replaced *subprocess* with native *git2* crate and achieved the
same result in much cleaner and safer way.

git2 is a native Rust crate which provides access to Git repository internals.
git2 does not involve any *unsafe* invocation as it is built against
*libgit2-sys* which is actually using Rust FFI to directly bind to underlying
libgit library. Below is the new *copyright_fromgit* function with git2 crate.

.. code-block:: rust

   fn copyright_fromgit(repo_url: &str) -> Result<String> {
      let tempdir = TempDir::new_in(".", "debcargo")?;
      let repo = Repository::clone(repo_url, tempdir.path())?;

      let mut revwalker = repo.revwalk()?;
      revwalker.push_head()?;

      // Get the latest and first commit id. This is bit ugly
      let latest_id = revwalker.next().unwrap()?;
      let first_id = revwalker.last().unwrap()?; // revwalker ends here is consumed by last

      let first_commit = repo.find_commit(first_id)?;
      let latest_commit = repo.find_commit(latest_id)?;

      let first_year =
          DateTime::<Utc>::from_utc(
                  NaiveDateTime::from_timestamp(first_commit.time().seconds(), 0),
                  Utc).year();

      let latest_year =
          DateTime::<Utc>::from_utc(
                NaiveDateTime::from_timestamp(latest_commit.time().seconds(), 0),
                Utc).year();

      let notice = match first_year.cmp(&latest_year) {
          Ordering::Equal => format!("{}", first_year),
          _ => format!("{}-{},", first_year, latest_year),
      };

      Ok(notice)
   }

So here is what I'm doing
 1. Use `git2::Repository::clone` to clone the given URL. We are thus avoiding
    exec of *git clone* command.

 2. Get a revision walker object. `git2::RevWalk` implements `Iterator` trait
    and allows walking through the git history. This is what we are using to
    avoid exec of *git log* command.

 3. `revwalker.push_head()` is important because we want to tell revwalker from
    where we want to walk the history. In this case we are asking it to walk
    history from repository HEAD. Without this line next line will not work.
    (Learned it in hard way :-) ).

 4. Then we extract `git2::Oid` which is we can say similar to commit hash and
    can be used to lookup a particular commit. We take latest commit hash using
    `RevWalk::next` call and the first commit using `Revwalk::last`, note the
    order this is because `Revwalk::last` consumes the revwalker so doing it in
    reverse order will make borrow checker unhappy :-). This replaces exec of
    `head -n1` command.

 5. Look up the `git2::Commit` objects using `git2::Repository::find_commit`

 6. Then  convert the `git2::Time` to `chrono::DateTime` and take out the years.


After this change I found an obvious error which went unnoticed in previous
version, that is if there was no *repository* key in Cargo.toml. When there was
no repo URL *git clone* exec did not error out and our shell commands happily
extracted year from the *debcargo* repository!. Well since I was testing code
from *debcargo* repository It never failed, but when I executed from non-git
repository folder git threw an error but that was *git log* and not *git
clone*. This error was spotted right away because git2 threw me an error that I
gave it empty URL.

When it comes to performance I see that debcargo is faster compared to previous
version. This makes sense because previously it was doing 5 fork and exec system
calls and now that is avoided.
