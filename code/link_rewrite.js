//
// Link Rewrite v1.0 by Postmodern (postmodern at sophsec.com)
//
// Catches the click event on all links and rewrites the href
// attribute to redirect the user to a specified link prefix.
// Requires jQuery (http://jquery.com/)
//

// prefix to rewrite the hrefs with
var link_prefix = "http://sophsec.com";

var protocol_regexp = /^\s*\w+:(\/\/)?/;
var absolute_regexp = /^\s*\//;

// URL protocols to target
var targeted_protocols = ["http", "https"];

function isLinkLocal(link) { return !protocol_regexp.test(link); }

function isLinkRelative(link)
{
	return (isLinkLocal(link) && !(absolute_regexp.test(link)));
}

function currentHostname() { return document.location.hostname; }

function currentDirectory()
{
	return document.location.pathname.replace(/[^\/]+$/,"");
}

function isLinkTargeted(link)
{
	if (isLinkLocal(link))
	{
		return true;
	}

	return (new RegExp("^\\s*(" + targeted_protocols.join("|") + "):")).test(link);
}

function convertLink(link)
{
	if (isLinkTargeted(link))
	{
		if (isLinkLocal(link))
		{
			if (isLinkRelative(link))
			{
				return link_prefix + '/' + currentHostname() + currentDirectory() + link;
			}

			return link_prefix + '/' + currentHostname() + link;
		}

		return link_prefix + '/' + link.replace(protocol_regexp,"");
	}

	return link;
}

$(document).ready(function() {
	$("a[@href]").click(function() {
		$(this).attr("href",convertLink($(this).attr("href")));
	});
});
