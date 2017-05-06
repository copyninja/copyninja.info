Magic: Attach a HTML file to mail and get different on other side
#################################################################

:date: 2017-05-06 13:19 +0530
:slug: fun-with-html-encoding
:tags: html, encoding
:author: copyninja
:summary: Magic happens when you attach HTML with certain format in mail and
          find totally different file on other end.

It's been a long time I did not write any new blog posts, and finally I got
something which is interesting enough for a new post and so here it is.

I actually wanted some bills from my ISP for some work and I could not find mail
from the ISP which had bills for some specific months in my mailbox. Problem
with my ISP is bills are accessible in their account which can be only accessed
from their own network. They do have a mobile app and that does not seem to work
especially for the billing section. I used mobile app and selected month for
which I did not have bill and clicked *Send Mail* button. App happily showed
message saying it sent the bill to my registered mail address but that was a
fancy lie. After trying several time I gave up and decided I will do it once I
get back home.

Fast forward few hours, I'm back home from office and then I sat in front of my
laptop and connected to ISP site, promptly downloaded the bills, then used
*notmuch-emacs* and fire up a mail composer, attach those HTML file (yeah they
produce bill in HTML file :-/) send it to my gmail and forget about it.

Fast forward few more days, I just remember I need those bills. I got hold of
mail I sent earlier in gmail inbox and clicked on attachment and when browser
opened the attachment I was shocked/surprised . Did you ask why?. See what I saw
when I opened attachment.

.. image:: {filename}/images/converted_html.png

Well I was confused for moment on what happened, I tried downloading the file
and opened it an editor, and I see Chinese characters here also. After reaching
home I checked the Sent folder in my laptop where I keep copy of mails sent
using *notmuch-emacs*'s `notmuch-fcc-dirs` variable. I open the file and open
the attachement and I see same character as I saw in browser!. I open the
original bills I downloaded and it looks fine. To check if I really attached the
correct files I again drafted a mail this time to my personal email and sent it.
Now I open the file from Sent folder and voila again there is different content
inside my attachment!. Same happens when I receive the mail and open the
attachment everything inside is Chinese characters!. Totally lost I finally
opened the original file using *emacs*, since I use *spacemacs* it asked me for
downloading of *html layer* and after which I was surprised because everything
inside the editor is in Chinese!. OK finally I've something now so I opened same
file at same time in *nano* from terminal and there it looks fine!. OK that is
weird again I read carefully content and saw this line in beginning of file

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-16" ?>
   <html xmlns="http://www.w3.org/1999/xhtml>....

OK that is new XML tag had encoding declared as *UTF-16*, really?. And just for
checking I changed it to UTF-8 and voila file is back to normal in Emacs
window!. To confirm this behavior I created a sample file with following content

.. code-block:: html

   <?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml"><head><meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" /><title> Something weird </title><body>blablablablablalabkabakba</body></html>

Yeah with long line because ISP had similar case and now I opened the same file
in nano using terminal and changed `encoding="UTF-8"` to `encoding="UTF-16"` and
the behavior repeated I see Chinese character in the emacs buffer which has also
opened the same file.

Below is the small gif showing this happening in real time, see what happens in
emacs buffer when I change the encoding in terminal below. Fun right?.

.. image:: {filename}/images/html_weirdness.gif

I made following observation from above experiments.

1. When I open original file in browser or my sample file with
   `encoding="UTF-16"` its normal, no Chinese characters.
2. When I attach the mail and send it out the attachment some how gets converted
   into HTML file with Chinese characters and viewing source from browser shows
   header containing xml declarations and original `<html>` declarations get
   ripped off and new tags show up which I've pasted below.

3. If I download the same file and open in editor only Chinese characters are
   present and no HTML tags inside it. So definitely the new tags which I saw by
   viewing source in browser is added by Firefox.

4. I create similar HTML file and change encoding I can see the characters
   changing back and forth in emacs *web-mode* when I change encoding of the
   file.

.. code-block:: html

   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
   <html>
     <head><META http-equiv="Content-Type"  content="text/html; charset=utf-8">

So if I'm understanding this correctly, *Emacs* due to encoding declaration
interprets the actual contents differently. To see how *Emacs* really
interpreted the content I opened the sent mail I had in raw format and saw
following header lines for attachment.

.. code-block:: ini

   Content-Type: text/html; charset=utf-8
   Content-Disposition: attachment;
                filename=SOA-102012059675-FEBRUARY-2017.html
   Content-Transfer-Encoding: base64

This was followed with base64 encoded data. So does this mean emacs interpreted
the content as UTF-16 and encoded the content using UTF-8?. Again I've no clue,
so I changed the `encoding` in both the files to be as UTF-8 and sent the mail
by attaching these files again to see what happens. And my guess was right I
could get the attachment as is on the receiving side. And inspecting raw mail
the attachment headers now different than before.

.. code-block:: ini

   Content-Type: text/html
   Content-Disposition: attachment;
                filename=SOA-102012059675-DECEMBER-2016.html
   Content-Transfer-Encoding: quoted-printable

See how *Content-Type* its different now also see the
*Content-Transfer-Encoding* its now `quoted-printable` as opposed to `base64`
earlier. Additionally I can see HTML content below the header.
When I opened the attachment from mail I get the actual bill.

As far as I understand base64 encoding is used when the data to be attached is
base64. So I guess basically due to wrong encoding declared inside the file
*Emacs* interpreted the content as a binary data and encoded it differently than
what it really should be. Phew that was a lot of investigation to understand the
magic but it was worth it.

Do let me know your thoughts on this.
