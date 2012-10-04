import	urllib2 
from	BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString, Comment
import collections
import tempfile
import webbrowser
import codecs
import os,sys
from  pprint import PrettyPrinter, pprint

sys.path.append(os.path.split(__file__)[0])
import scrapers

def identity(x):
	print x
	return x

def auth(topurl, theurl):
	username = 'boggob'
	password = 'slobodan'
	# a great password

	passman = urllib2.HTTPPasswordMgr()
	# this creates a password manager
	passman.add_password("musicbrainz.org", topurl, username, password)
	# because we have put None at the start it will always
	# use this username/password combination for  urls
	# for which `theurl` is a super-url

	authhandler = urllib2.HTTPBasicAuthHandler(passman)
	# create the AuthHandler

	opener = urllib2.build_opener(authhandler)
	urllib2.install_opener(opener)

	return opener.open(theurl).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

	#urllib2.install_opener(opener)
	
def geturl(url):
	#, headers = {"Accept-Encoding":"gzip"}
	print "getting: %s" % url
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def contents_flatten(tags):
	out = []
	for tag in tags:
		if isinstance(tag, Comment):
			pass
		elif isinstance(tag, NavigableString):
			s =tag.strip() 
			if s:
				out.append(s)
		elif hasattr(tag, 'name') and (
			(tag.name == 'font' and tag['size'] == "1") 
			or
			(tag.name == 'script') 
		):
			pass
		else:
			out.extend(contents_flatten(tag.contents))
	return out
		

def scrape(html):
	def records(worksin):
		out		= []
		for idx, ww in  enumerate(worksin):		
			works = {}
			
			works['works'] =  contents_flatten(ww)
			comp = ww.findPrevious('p', {'class' : 'composers'})
			if comp and	comp['class'] == 'composers':
				works['composers']	= [c.string.strip() for c in comp.findAll('a')]
			
			tagm = ww.findNextSibling('div', {'class' : 'performers'})

			works['performers']	=	{
										td.a.string.strip() : "".join(
																		tdc 
																		for tdc in td.contents 
																		if isinstance(tdc, NavigableString)
																).replace(',', '').strip() 
										for td in tagm.findAll('td') 
										if td.a
									}
			ttags = tagm.findNextSiblings(lambda ent: ent and ent.name in ('div', 'table'))
			
			works['tracks']	= []
			for ttag in ttags:
				if  ttag.name != 'table':
					break
				dat = contents_flatten(ttag)
				if dat:
					works['tracks'].append(dat)
			
			out.append(works)
			
			
		return out
		
	
	soup = BeautifulSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
	d  =  soup.find('td', { 'class' : "style5"})
	
	if not d:
		return None
	else:
		
	
		out = {
			'headers'  : [
							[x for x in contents_flatten(p) if x != u';']
							for p in d.findAll('p')
						],
			'title' 	: soup.find('h1', {'class':"cdtitle"})gvfbhjml;./-.string.strip(),
			'works' 	: records(soup.findAll('div', {'class':"works"}))
		}
	
	return out


def artist_sort_order(artists):
	return [" ".join(s.strip() for s in artist.split(',')[::-1]) for artist in artists]
	
def transform(cluster):
	out = {}
	
	out['title']			= cluster['title']
	
	headers 				= dict(
								(
									(items[0], [x for x in items[1:] if x != ':'])
										if len(items) > 1 else
									items[0].split(':')
								)
								for items in cluster['headers']
							)
	#pprint(headers)
	out['label']			= headers['Label'][0].strip()
	out['barcode']			= headers['Barcode'][0][1:].strip()
	out['catalognumber']	= headers['Catalogue No'].strip()
	date					= headers['Physical Release'][0].replace(':','').strip()
	out['year']				= date.split('/')[-1]
	out['month']			= date.split('/')[0]
	out['tags']				= headers['Genre']
	out['albumartist']		= artist_sort_order(headers['Composer(s)'])
	
		
	out['tracks']			= [ 
								{
									'number'		: int(track[0].split('.')[0]),
									'title'			: "{}: {}".format(work['works'][0], track[1]) if work['works'][0] != track[1] else track[1],
									'artist'		: artist_sort_order(work['composers']), 
									'performers'	: {artist_sort_order([a])[0] : i for a,i in work['performers'].iteritems()}, 
									'length'		: track[-1],
								} 
								for work in cluster['works']
								for track in work['tracks']
								if len(track[0].split('.')) > 1
							]
	return out
################################################################################################################################################
def esc(s):
	return "".join(
				{
					"&": "&amp;",
					'"': "&quot;"
				}.get(c, c) 
				for c in s
			)

def nv(n, v):
	return """<input type="hidden" name="%s" value="%s">""" % (esc(n), esc(v))
	
	
def webify(cluster):
	out = []
	
	out.append("""<!doctype html>
	<meta charset="UTF-8">
	<title>Add Cluster As Release</title>
	<form action="http://musicbrainz.org/release/add" method="post">
	""")
	for form, func in {
		("name"						, lambda cl: cl['title']),
		("labels.0.name"			, lambda cl: cl['label']),
		('barcode'					, lambda cl: cl["barcode"]),
		("date.year"				, lambda cl: cl['year']),
		("date.month"				, lambda cl: cl['month']),
		("labels.0.catalog_number"	, lambda cl: cl['catalognumber']),
		#English - latin
		("language_id"				, lambda cl: "120"),
		("script_id"				, lambda cl: "28"),
		#official,album jewel case 
		("status_id"				, lambda cl: "1"),
		("primary_type_id"			, lambda cl: "1"),
		("packaging_id"				, lambda cl: "1"),
		
	}:
		out.append(nv(form, func(cluster)))

	if cluster['albumartist']:
		artnames = [albn.strip() for albn in cluster['albumartist']]
		for idx, artname in enumerate(artnames): 
			out.append(nv("artist_credit.names.%d.artist.name" % (idx), artname))
			if idx + 1 < len(artnames):
				out.append(nv("artist_credit.names.%d.join_phrase" % (idx), " & "))
	
	for medium in [0]:
		out.append(nv("mediums.%d.format_id" % medium, '1'))
		for trk in cluster['tracks']:
			label = "mediums.%d.track.%d.%%s" % (medium, int(trk['number'])  -1)
			out.append(nv(label % 'name', trk["title"]))
			out.append(nv(label % 'length', trk["length"]))
			if trk["artist"] != cluster['albumartist']:
				for idx, artist in enumerate(trk["artist"]):
					out.append(nv(label % 'artist_credit.names.%d.name' % idx, artist))
					out.append(nv(label % 'artist_credit.names.%d.joinphrase' % idx, ' & '))
					
	out.append("""<input type="submit" value="Add Release">
	</form>
	<script>document.forms[0].submit()</script>
	""")
	return "\n".join(out)





#<option value="156">{additional:additionally} {guest} {solo} performed
#<option value="148">performed {additional} {guest} {solo} {instrument} on
#<option value="149">performed {additional} {solo} {guest} {vocal} vocal on
#<option value="150">{orchestra} orchestra {additional:additionally} performed
#<option value="151">{additional:additionally} conducted
#<option value="152">performed {additional} chorus master on

name_linktype_map = {
	'instrument'	: "148",
	''				: "156",
	'conducted'		: "151",
	'vocal'			: "149",
}

instrument_map = {
	"15"			: "wind instruments",
	"16"			: "woodwind",
	"233"			: "reeds",
	"17"			: "double reed",
	"18"			: "bagpipe",
	"514"			: "bellow-blown bagpipes",
	"248"			: "uilleann pipes",
	"438"			: "Northumbrian pipes",
	"513"			: "Scottish smallpipes",
	"515"			: "practice chanter",
	"519"			: "bombarde",
	"606"			: "dulcian",
	"19"			: "bassoon",
	"609"			: "piri",
	"622"			: "cornamuse",
	"334"			: "kortholt",
	"20"			: "contrabassoon",
	"492"			: "zurna",
	"493"			: "shawm",
	"22"			: "oboe",
	"581"			: "oboe d&#39;amore",
	"604"			: "shehnai",
	"21"			: "english horn",
	"261"			: "heckelphone",
	"380"			: "ken bau",
	"427"			: "crumhorn",
	"480"			: "duduk",
	"234"			: "singular reed",
	"23"			: "clarinet",
	"24"			: "alto clarinet",
	"488"			: "soprano clarinet",
	"490"			: "basset horn",
	"489"			: "basset clarinet",
	"25"			: "bass clarinet",
	"26"			: "contrabass clarinet",
	"33"			: "saxophone",
	"537"			: "sopranino saxophone",
	"34"			: "soprano saxophone",
	"35"			: "alto saxophone",
	"36"			: "tenor saxophone",
	"37"			: "baritone saxophone",
	"536"			: "bass saxophone",
	"538"			: "contrabass saxophone",
	"532"			: "taragot",
	"63"			: "free reed",
	"104"			: "jew&#39;s harp",
	"592"			: "bawu",
	"64"			: "accordion",
	"439"			: "piano accordion",
	"520"			: "bayan",
	"521"			: "chromatic button accordion",
	"440"			: "button accordion",
	"441"			: "diatonic accordion / melodeon",
	"65"			: "concertina",
	"66"			: "harmonica",
	"376"			: "chromatic harmonica",
	"558"			: "bass harmonica",
	"396"			: "ding nam",
	"395"			: "khen meo",
	"263"			: "bandoneon",
	"67"			: "melodica",
	"68"			: "sheng",
	"262"			: "sho",
	"384"			: "ki pah",
	"389"			: "hmong flute",
	"385"			: "tram ple",
	"390"			: "trang lu",
	"391"			: "trang jau",
	"392"			: "pang gu ly hu hmong",
	"393"			: "sao meo",
	"394"			: "dinh taktar",
	"388"			: "khen la ",
	"524"			: "chalumeau",
	"27"			: "flute",
	"422"			: "transverse flute",
	"31"			: "piccolo",
	"603"			: "nohkan",
	"626"			: "fife",
	"497"			: "treble flute",
	"498"			: "soprano flute",
	"499"			: "concert flute",
	"500"			: "flute d&#39;amour",
	"423"			: "alto flute",
	"501"			: "bass flute",
	"502"			: "Indian bamboo flutes",
	"251"			: "bansuri",
	"503"			: "venu",
	"269"			: "sao truc",
	"553"			: "dizi",
	"564"			: "shinobue",
	"602"			: "daegeum",
	"28"			: "end-blown flute",
	"30"			: "pan flute",
	"370"			: "syrinx",
	"369"			: "nai",
	"224"			: "shakuhachi",
	"401"			: "tieu flute",
	"416"			: "pi thiu",
	"528"			: "quena",
	"551"			: "kaval",
	"593"			: "xiao",
	"264"			: "duct flutes",
	"625"			: "spilapipa",
	"32"			: "recorder",
	"361"			: "garklein recorder",
	"362"			: "sopranino recorder",
	"563"			: "descant recorder / soprano recorder",
	"363"			: "treble recorder / alto recorder",
	"364"			: "tenor recorder",
	"365"			: "bass recorder / f-bass recorder",
	"366"			: "great bass recorder / c-bass recorder",
	"367"			: "contrabass recorder",
	"368"			: "subcontrabass recorder",
	"266"			: "willow flute",
	"267"			: "tin whistle",
	"482"			: "low whistle",
	"268"			: "slide whistle",
	"265"			: "other flutes",
	"620"			: "algozey",
	"383"			: "ding buot",
	"387"			: "sao oi flute",
	"29"			: "ocarina",
	"270"			: "nose flute",
	"355"			: "k&#39;long put",
	"504"			: "boatswain&#39;s pipe",
	"38"			: "brass",
	"271"			: "valved brass instruments",
	"47"			: "trumpet",
	"486"			: "piccolo trumpet",
	"39"			: "cornet",
	"43"			: "flugelhorn",
	"56"			: "mellophone",
	"40"			: "horn",
	"44"			: "french horn",
	"42"			: "baritone horn",
	"45"			: "tenor horn / alto horn",
	"48"			: "tuba",
	"199"			: "euphonium",
	"200"			: "sousaphone",
	"201"			: "Wagner tuba",
	"272"			: "slide brass instruments",
	"46"			: "trombone",
	"228"			: "bass trombone",
	"237"			: "valve trombone",
	"198"			: "sackbut",
	"203"			: "keyed brass instruments",
	"197"			: "serpent",
	"273"			: "cornett",
	"49"			: "natural brass instruments",
	"51"			: "bugle",
	"41"			: "alphorn",
	"60"			: "shofar",
	"205"			: "conch",
	"204"			: "didgeridoo",
	"57"			: "ophicleide",
	"615"			: "jug",
	"176"			: "organ",
	"539"			: "electronic organ",
	"177"			: "Hammond organ",
	"540"			: "farfisa",
	"600"			: "barrel organ",
	"179"			: "pipe organ",
	"565"			: "chamber organ",
	"274"			: "reed organ",
	"178"			: "harmonium",
	"535"			: "shruti box",
	"170"			: "calliope",
	"426"			: "theatre organ",
	"69"			: "strings",
	"275"			: "bowed string instruments",
	"118"			: "viola da gamba",
	"276"			: "rebec",
	"71"			: "double bass (contrabass, acoustic upright bass)",
	"72"			: "electric upright bass",
	"119"			: "viola d&#39;amore",
	"505"			: "violone",
	"82"			: "violins",
	"84"			: "cello",
	"278"			: "electric cello",
	"87"			: "viola",
	"86"			: "violin",
	"279"			: "treble violin",
	"280"			: "soprano violin",
	"226"			: "alto violin",
	"120"			: "violotta",
	"85"			: "fiddle",
	"102"			: "hardingfele",
	"281"			: "kemenche",
	"613"			: "kamancheh",
	"282"			: "electric violin",
	"116"			: "vielle",
	"543"			: "Stroh violin",
	"283"			: "huqin",
	"284"			: "jing hu",
	"595"			: "haegeum",
	"285"			: "erhu",
	"286"			: "gaohu",
	"287"			: "zhonghu",
	"288"			: "cizhonghu",
	"289"			: "gehu",
	"290"			: "diyingehu",
	"291"			: "banhu / banghu",
	"292"			: "yehu",
	"293"			: "kokyu",
	"294"			: "morin khuur / matouqin",
	"295"			: "dan nhi",
	"386"			: "koke",
	"296"			: "archaic and other bowed string-instruments",
	"297"			: "viola organista",
	"552"			: "sarangi",
	"591"			: "Cretan lyra",
	"98"			: "crwth",
	"298"			: "nyckelharpa",
	"299"			: "bowed psaltery",
	"300"			: "gudok",
	"301"			: "gadulka",
	"190"			: "musical saw",
	"302"			: "plucked string instruments",
	"75"			: "guitars",
	"229"			: "guitar",
	"77"			: "classical guitar",
	"76"			: "acoustic guitar",
	"206"			: "Spanish acoustic guitar",
	"522"			: "tenor guitar",
	"79"			: "slide guitar",
	"80"			: "steel guitar",
	"466"			: "lap steel guitar",
	"470"			: "electric lap steel guitar",
	"78"			: "electric guitar",
	"467"			: "resonator guitar",
	"240"			: "dobro",
	"468"			: "table steel guitar",
	"469"			: "pedal steel guitar",
	"377"			: "baritone guitar",
	"529"			: "12 string guitar",
	"399"			: "Vietnamese guitar",
	"400"			: "Hawaiian guitar",
	"277"			: "bass guitar",
	"73"			: "acoustic bass guitar",
	"523"			: "fretless bass",
	"74"			: "electric bass guitar",
	"303"			: "dan tu day",
	"331"			: "tiple",
	"117"			: "Mexican vihuela",
	"531"			: "cuatro",
	"114"			: "ukulele",
	"115"			: "tres",
	"332"			: "Spanish vihuela",
	"623"			: "tumbi",
	"95"			: "bouzouki",
	"491"			: "Irish bouzouki",
	"108"			: "lute",
	"304"			: "oud",
	"94"			: "biwa",
	"495"			: "cumbus",
	"478"			: "theorbo",
	"556"			: "tzoura",
	"559"			: "charango",
	"560"			: "tar (lute)",
	"566"			: "saz",
	"512"			: "baglama",
	"305"			: "Turkish baglama",
	"306"			: "Greek baglama",
	"585"			: "Saraswati veena",
	"586"			: "tanbur",
	"473"			: "tambura",
	"474"			: "tamburitza",
	"594"			: "domra",
	"308"			: "mandola",
	"96"			: "mandolin",
	"91"			: "balalaika",
	"475"			: "bandura",
	"598"			: "bandora",
	"611"			: "rudra veena",
	"619"			: "archlute",
	"307"			: "cittern",
	"309"			: "rebab",
	"250"			: "sarod",
	"402"			: "gumbri",
	"122"			: "xalam / khalam",
	"92"			: "banjo",
	"479"			: "banjitar",
	"310"			: "moon lute",
	"311"			: "zhongruan",
	"312"			: "dan nguyet",
	"414"			: "dan tam",
	"429"			: "pipa",
	"313"			: "dan ty ba",
	"314"			: "sanxian",
	"315"			: "sanshin",
	"112"			: "shamisen",
	"113"			: "sitar",
	"316"			: "electric sitar",
	"109"			: "lyre",
	"317"			: "kinnor",
	"318"			: "kithara",
	"81"			: "harp",
	"431"			: "concert harp",
	"432"			: "electric harp",
	"433"			: "folk harp",
	"435"			: "Irish harp / clarsach",
	"436"			: "german harp",
	"434"			: "wire-strung harp",
	"111"			: "psaltery",
	"174"			: "harpsichord",
	"621"			: "virginal",
	"106"			: "kora",
	"123"			: "zither",
	"90"			: "Appalachian dulcimer",
	"544"			: "zheng",
	"320"			: "dan tranh",
	"616"			: "guqin",
	"100"			: "geomungo",
	"107"			: "koto",
	"628"			: "17-string koto",
	"99"			: "gayageum",
	"506"			: "Baltic psalteries",
	"507"			: "kankles",
	"508"			: "gusli",
	"509"			: "kantele",
	"319"			: "langeleik",
	"360"			: "kanun",
	"321"			: "dan bau",
	"476"			: "bandura",
	"494"			: "autoharp",
	"534"			: "marxophone",
	"97"			: "musical bow",
	"93"			: "berimbau",
	"322"			: "struck string instruments",
	"101"			: "hammered dulcimer",
	"326"			: "cymbalum",
	"324"			: "yangqin",
	"359"			: "khim",
	"325"			: "santur",
	"327"			: "dan tam thap luc",
	"358"			: "santoor",
	"238"			: "Chapman stick",
	"323"			: "Warr guitar",
	"173"			: "clavichord",
	"227"			: "clavinet",
	"180"			: "piano",
	"465"			: "fortepiano",
	"614"			: "bowed piano",
	"510"			: "tangent piano",
	"181"			: "grand piano",
	"184"			: "upright piano",
	"328"			: "toy piano",
	"329"			: "electric piano",
	"182"			: "Rhodes piano",
	"562"			: "Wurlitzer electric piano",
	"330"			: "Chamberlin",
	"175"			: "Mellotron",
	"232"			: "keyboard",
	"442"			: "keyboard bass",
	"590"			: "prepared piano",
	"88"			: "other string instruments",
	"89"			: "aeolian harp",
	"103"			: "hurdy gurdy",
	"121"			: "washtub bass",
	"124"			: "percussion",
	"125"			: "drums",
	"126"			: "drumset",
	"487"			: "electronic drum set",
	"397"			: "brushes",
	"483"			: "dohol",
	"518"			: "bass drum",
	"550"			: "Bata drum",
	"555"			: "tom-tom",
	"584"			: "mridangam",
	"612"			: "pakhavaj",
	"589"			: "thavil",
	"601"			: "cuica",
	"605"			: "janggu",
	"421"			: "frame drum",
	"333"			: "tambourine",
	"406"			: "rek",
	"583"			: "kanjira",
	"403"			: "daf",
	"420"			: "bendir",
	"249"			: "bodhran",
	"496"			: "davul",
	"456"			: "ocean drum",
	"127"			: "congas",
	"128"			: "bongos",
	"335"			: "djembe",
	"140"			: "doyra",
	"338"			: "goblet drum",
	"241"			: "tabla",
	"405"			: "zarb",
	"419"			: "darbuka",
	"382"			: "trong bong",
	"242"			: "madal",
	"413"			: "cajon",
	"447"			: "vessel drum",
	"407"			: "udu",
	"408"			: "ghatam",
	"458"			: "taiko",
	"410"			: "tanbou ka",
	"336"			: "dai co/tieu co",
	"129"			: "snare drum",
	"463"			: "dholak",
	"217"			: "timpani",
	"459"			: "surdo",
	"457"			: "talking drum",
	"446"			: "slit drum",
	"337"			: "mo",
	"150"			: "tuned percussion",
	"151"			: "bells",
	"346"			: "handbells",
	"597"			: "agogo",
	"218"			: "tubular bells",
	"208"			: "cowbell",
	"171"			: "carillon",
	"464"			: "gankogui",
	"339"			: "gongs",
	"340"			: "gong",
	"608"			: "kkwaenggwari",
	"342"			: "cymbals",
	"343"			: "nao bat / chap choa",
	"547"			: "hi-hat",
	"554"			: "finger cymbals",
	"548"			: "zill",
	"220"			: "xylophone",
	"216"			: "marimba",
	"215"			: "glockenspiel",
	"214"			: "crotales",
	"172"			: "celesta",
	"445"			: "gamelan",
	"451"			: "bamboo angklung",
	"452"			: "metal angklung",
	"381"			: "t&#39;rung",
	"443"			: "amadinda",
	"444"			: "balafon",
	"428"			: "metallophone",
	"219"			: "vibraphone",
	"409"			: "ti bwa",
	"132"			: "timbales",
	"344"			: "steelpan",
	"133"			: "triangle",
	"345"			: "whistle",
	"110"			: "mbira",
	"191"			: "singing bowl",
	"415"			: "chimes",
	"221"			: "other percussion",
	"136"			: "afuche / cabasa",
	"588"			: "bell tree",
	"607"			: "wind chime",
	"624"			: "hang",
	"411"			: "rattle",
	"142"			: "maracas",
	"412"			: "chacha",
	"450"			: "sistrum",
	"453"			: "ankle rattlers",
	"462"			: "shekere",
	"455"			: "rainstick",
	"417"			: "shakers",
	"599"			: "caxixi",
	"137"			: "castanets",
	"210"			: "spoons",
	"356"			: "song loan",
	"437"			: "bones",
	"138"			: "claves",
	"449"			: "rhythm sticks",
	"347"			: "sanh tien",
	"379"			: "phach",
	"418"			: "sapek clappers",
	"460"			: "bin-sasara",
	"141"			: "guiro",
	"143"			: "mendoza",
	"211"			: "ratchet",
	"212"			: "vibraslap",
	"209"			: "washboard",
	"448"			: "frottoir",
	"134"			: "whip",
	"213"			: "wood block",
	"222"			: "temple blocks",
	"350"			: "Tibetan water drum",
	"351"			: "waterphone",
	"610"			: "body percussion",
	"398"			: "handclaps",
	"541"			: "finger snaps",
	"587"			: "foot percussion",
	"159"			: "electronic instruments",
	"160"			: "Denis d&#39;or",
	"627"			: "laser harp",
	"161"			: "Dubreq Stylophone",
	"162"			: "drum machine",
	"404"			: "ebow",
	"533"			: "EWI",
	"163"			: "ondes Martenot",
	"352"			: "omnichord",
	"164"			: "sampler",
	"165"			: "synclavier",
	"166"			: "synthesizer",
	"348"			: "Moog",
	"549"			: "bass synthesizer",
	"349"			: "Minimoog",
	"471"			: "continuum",
	"167"			: "teleharmonium",
	"168"			: "theremin",
	"354"			: "vocoder",
	"454"			: "wavedrum",
	"484"			: "bass pedals",
	"542"			: "voice synthesizer",
	"185"			: "other instruments",
	"192"			: "suikinkutsu",
	"202"			: "bull-roarer",
	"546"			: "talkbox",
	"557"			: "musical box",
	"70"			: "bass",
	"236"			: "turntable(s)",
	"187"			: "hardart",
	"189"			: "lasso d&#39;amore",
	"188"			: "kazoo",
	"357"			: "glass (h)armonica",
	"375"			: "vacuum cleaner",
}
vocals_map = {
	"4"			: "lead",
	"5"			: "alto",
	"230"		: "contralto",
	"231"		: "bass-baritone",
	"6"			: "baritone",
	"7"			: "bass",
	"8"			: "contra-tenor",
	"9"			: "mezzo-soprano",
	"10"		: "soprano",
	"11"		: "tenor",
	"13"		: "choir",
	"12"		: "background",
	"461"		: "other",
	"561"		: "spoken",
}
	
	
def webify_ars(cluster, mbid_release):
	print "#" * 120
	url = 'http://musicbrainz.org/edit/relationship/create-recordings?release={mbid}&type=artist&gid={ambid}'.format(mbid =mbid_release, ambid = '89ad4ac3-39f7-470e-963a-56509c546377')
	val =  auth('http://musicbrainz.org', url)
	print val
	recording_map = {
		idx : cb['value'] 
		for idx, cb in enumerate(
			BeautifulSoup(
				identity(val)
			).findAll('input', {'name' :"recording_id"})
		)
	}
	print "***", recording_map

	raise 1	
		
	recording_map = {
		idx : cb['value'] 
		for idx, cb in enumerate(
			BeautifulSoup(
				identity(geturl(url))
			).findAll('input', {'name' :"recording_id"})
		)
	}
	print "***", recording_map
	raise 1	
	
	aggr = collections.defaultdict(list)
	for trk in cluster['tracks']:
		for perf,instr in trk["performers"].iteritems():
			aggr[perf,instr].append(int(trk['number'])  -1)
	
	outs = []
	for (perf, instr), tracks in aggr.iteritems():
		mbid = scrapers.brainz_lookup_artist_mb(perf,[],True)
		out = []
		out.append( 
			"""<!doctype html>
			<meta charset="UTF-8">
			<title>Add Cluster As Release</title>
			<form action="http://musicbrainz.org/edit/relationship/create-recordings?{}" method="post">
			""".format(
					"&".join((
						"release=".format(mbid_release),
						"type=artist",
						"gid={}".format(mbid)
					))				
				)
		)
		
		if instr in instrument_map:
			out.append( """<input type="hidden" name="ar.link_type_id" value="%s">""" % name_linktype_map['instrument'])
			out.append( """<input type="hidden" name="ar.attrs.instrument.0" value="%s">""" % instr)
		if instr in vocals_map:
			out.append( """<input type="hidden" name="ar.link_type_id" value="%s">""" % name_linktype_map['vocal'])
			out.append( """<input type="hidden" name="ar.attrs.vocal.0" value="%s">""" % instr)		
		
		for track in tracks:
			out.append( """<input type="hidden" name="recording_id" value="%s">""" % recording_map[track])
	 
		out.append("""
			</form>
			"""
		)
		outs.append(out)
	return outs	
		
	
def temp_create(out):
	(fd, fp) = tempfile.mkstemp(suffix=".html")
	f = codecs.getwriter("utf-8")(os.fdopen(fd, "w"))
	f.write(out)
	f.close()
	return fp

def post(out):
	webbrowser.open("file://"+temp_create(out))
################################################################################################################################################################################################################
def scrape_and_post(url):
	post(webify(transform(scrape(url))))
				
def clean(html_crappy):
		import subprocess		
		fp = temp_create(html_crappy)
		with open(os.devnull, "w") as fnull:
			xx = subprocess.call(	args = (r'c:\apps\tidy\tidy.exe', '-asxml', '-w', '-i', '-m', fp), stdin= subprocess.PIPE, stderr=fnull,stdout=fnull,  shell= False)
		with open(fp) as fd:
			with open('c:/temp/b.html','w') as ff:
				html = fd.read()
				ff.write(html)
			
		return html

if __name__ == "__main__":
	for url in (
		'file:///c:/temp/a.html',
		'http://www.naxos.com/catalogue/item.asp?item_code=8.550194',
		'http://www.naxos.com/catalogue/item.asp?item_code=8.550651',
		'http://www.naxos.com/catalogue/item.asp?item_code=8.556711',
		'http://www.naxos.com/catalogue/item.asp?item_code=8.556707'
	):
		html =  clean(geturl(url))
		x = scrape(html)
		pprint(x)
		print
		xx = transform(x)
		pprint(xx)
		print
		x = webify(xx)
		#print(x)
		
		x = webify_ars(xx, 'c23bf70d-b167-4125-8b26-c1c1729cc9b0')
		print(x)
		print "#" * 100

		
		break
	
	

