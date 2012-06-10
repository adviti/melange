<?php include '../includes/header.php'?>

<p>Ready? Here we go. <strong>Strong text (<code>&#60;&#115;&#116;&#114;&#111;&#110;&#103;&#62;</code>)</strong>. <em>Italic (<code>&#60;&#101;&#109;&#62;</code>) text</em>. <del datetime="2007-05-20T04:13:55+00:00">This text has been deleted, but we want to keep a record of it.</del> We use the <code>&#60;&#100;&#101;&#108;&#62;</code> tag. <ins datetime="2007-05-20T04:13:55+00:00">The new text should be wrapped in an insert (<code>&#60;&#105;&#110;&#115;&#62;</code>) tag.</ins> <a href="http://www.w3schools.com/tags/tag_ins.asp">Read more about using these tags</a>. <mark>The mark tag (<code>&#60;&#109;&#97;&#114;&#107;&#62;</code>) can be used to highlight important text.</mark> The <code>&#60;&#97;&#98;&#98;&#114;&#62;</code> tag lets you know that the <abbr title="Basement"><a href="http://www.example.com/abbr">BSMT</a></abbr> is in the <abbr title="Apartment">APT</abbr>.</p>
<blockquote><p>Use the <code>&#60;&#98;&#108;&#111;&#99;&#107;&#113;&#117;&#111;&#116;&#101;&#62;</code> tag for quotes. Awkward grammar appals a craftsman. A Dada bard as daft as Tzara damns stagnant art and scrawls an alpha (a slapdash arc and a backward zag) that mars all stanzas and jams all ballads.</p></blockquote>
<blockquote><p>This is a one-line quote.</p></blockquote>
<q>This is the default styling of the <code>&#60;&#113;&#62;</code> tag.</q>
<h1>This is a h1 tag. Use of this tag is not recommended; the page title is already set as the h1.</h1>
<h2>This is a h2 tag</h2>
<p>"What has he in his hand there?" cried Starbuck, pointing to something wavingly held by the German. "Impossible!&mdash;a lamp-feeder!"</p>
<h3>This is a h3 tag</h3>
<p>"Not that," said Stubb, "no, no, it's a coffee-pot, Mr. Starbuck; he's coming off to make us our coffee, is the Yarman; don't you see that big tin can there alongside of him?&mdash;that's his boiling water. Oh! he's all right, is the Yarman."</p>
<h4>This is an h4 tag</h4>
<p>"Go along with you," cried Flask, "it's a lamp-feeder and an oil-can. He's out of oil, and has come a-begging."</p>
<h5>This is a h5 tag</h5>
<p>However curious it may seem for an oil-ship to be borrowing oil on the whale-ground, and however much it may invertedly contradict the old proverb about carrying coals to Newcastle...</p>
<h6>This is a h6 tag</h6>
<p>... yet sometimes such a thing really happens; and in the present case Captain Derick De Deer did indubitably conduct a lamp-feeder as Flask did declare.</p>
<ul>
<li>An unordered list</li>
<li>Morbi gravida
<ul><li>Second level</li><li>Neque libero elementum nunc</li><li>Enim ullamcorper<ul><li>Third level</li><li>Quis justo tempor feugiat in imperdiet</li><li>Phasellus consectetur massa</li></ul></li><li>Suspendisse blandit erat at metus</li></ul></li>
<li>Condimentum ligula lacinia</li>
</ul>
<ol>
<li>An ordered list</li>
<li>First level
<ol><li>Second level</li><li>Nunc non dictum eros<ol><li>Third level</li><li>Sem et enim malesuada porta<ol><li>Fourth level</li><li>Donec malesuada tempus laoreet</li></ol></li><li>Curabitur aliquam tortor eu tortor pharetra mattis</li></ol></li><li>Elit scelerisque vel blandit ligula placerat</li></ol></li>
<li>Quam in elit scelerisque</li>
</ol>
<dl>
<dt>This is a definition list</dt>
<dd>A <a href="http://www.benmeadowcroft.com/webdev/articles/definition-lists.shtml">definition list</a> is a list of definitions. It is composed of three HTML elements: the container tag (<code>&#60;&#100;&#108;&#62;</code>), the term being defined (<code>&#60;&#100;&#116;&#62;</code>) and the definition (<code>&#60;&#100;&#100;&#62;</code>).</dd>
<dt>Lychee</dt>
<dd>Coming from an evergreen tree, the lychee or litchi are small white flesh fruits, covered in a red rind, rich in vitamin C and with a grape-like texture. The fruit has started making its appearance in markets worldwide, refrigerated or canned with its taste intact.</dd>
<dt>Mangosteen</dt>
<dd>The mangosteen is another evergreen tree that produces oddly shaped fruits. The fruits are purple, creamy, described as citrus with a hint of peach. It is rich in antioxidants, some scientists even suggesting it can lower risk against certain human diseases, such as cancer. There are even legends about Queen Victoria offering a reward to the one that brings her the fruit.</dd>
</dl>
<hr>
<p>Present css using <code>&#60;&#99;&#111;&#100;&#101;&#62;</code> inside <code>&#60;&#112;&#114;&#101;&#62;</code>:</p>
<pre><code>strong {
    color: #333;
    font-weight: bold;
}</code></pre>

<p>Presenting code using only a <code>&#60;&#112;&#114;&#101;&#62;</code> tag:</p>
<pre>// Use of the pre element for PHP code
function sandbox_blog_lang() {
	if ( function_exists('language_attributes') )
		return language_attributes();
}</pre>
<hr>
<table>
<tbody>
<tr>
<th>Table Header 1</th>
<th>Table Header 2</th>
<th>Table Header 3</th>
</tr>
<tr>
<td>Division 1</td>
<td>Division 2</td>
<td>Division 3</td>
</tr>
<tr class="even">
<td>Division 1</td>
<td>Division 2</td>
<td>Division 3</td>
</tr>
<tr>
<td>Division 1</td>
<td>Division 2</td>
<td>Division 3</td>
</tr>
</tbody>
</table>
<hr>
<p>A last paragraph. Quisque ut odio auctor lorem tincidunt sodales. Vestibulum aliquet tristique vestibulum. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. In vel congue risus. Proin ultricies condimentum egestas. Curabitur quis leo sem, sit amet volutpat nibh. Donec non neque nec justo mollis dapibus in non purus.</p>

<?php include '../includes/footer.php'?>