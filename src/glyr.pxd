from libcpp cimport bool

cdef extern from "glyr/glyr.h":

###########################################################################
#                                callbacks                                #
###########################################################################

    # This also includes glyr/types.h
    ctypedef int (* DL_callback) (GlyrMemCache * c, GlyrQuery * s)
    ctypedef int (*glyr_foreach_callback)(GlyrQuery * q, GlyrMemCache * item, void * userptr)

###########################################################################
#                                  Enums                                  #
###########################################################################

    ctypedef enum GLYR_NORMALIZATION:
        NORMALIZE_NONE       "GLYR_NORMALIZE_NONE"
        NORMALIZE_MODERATE   "GLYR_NORMALIZE_MODERATE"
        NORMALIZE_AGGRESSIVE "GLYR_NORMALIZE_AGGRESSIVE"
        NORMALIZE_ARTIST     "GLYR_NORMALIZE_ARTIST"
        NORMALIZE_ALBUM      "GLYR_NORMALIZE_ALBUM"
        NORMALIZE_TITLE      "GLYR_NORMALIZE_TITLE"
        NORMALIZE_ALL        "GLYR_NORMALIZE_ALL"


    ctypedef enum GLYR_DATA_TYPE:
        TYPE_NOIDEA           "GLYR_TYPE_NOIDEA"
        TYPE_LYRICS           "GLYR_TYPE_LYRICS"
        TYPE_ALBUM_REVIEW     "GLYR_TYPE_ALBUM_REVIEW"
        TYPE_ARTIST_PHOTO     "GLYR_TYPE_ARTIST_PHOTO"
        TYPE_COVERART         "GLYR_TYPE_COVERART"
        TYPE_ARTISTBIO        "GLYR_TYPE_ARTISTBIO"
        TYPE_SIMILAR_ARTIST   "GLYR_TYPE_SIMILAR_ARTIST"
        TYPE_SIMILAR_SONG     "GLYR_TYPE_SIMILAR_SONG"
        TYPE_ALBUMLIST        "GLYR_TYPE_ALBUMLIST"
        TYPE_TAG              "GLYR_TYPE_TAG"
        TYPE_TAG_ARTIST       "GLYR_TYPE_TAG_ARTIST"
        TYPE_TAG_ALBUM        "GLYR_TYPE_TAG_ALBUM"
        TYPE_TAG_TITLE        "GLYR_TYPE_TAG_TITLE"
        TYPE_RELATION         "GLYR_TYPE_RELATION"
        TYPE_IMG_URL          "GLYR_TYPE_IMG_URL"
        TYPE_TXT_URL          "GLYR_TYPE_TXT_URL"
        TYPE_TRACK            "GLYR_TYPE_TRACK"
        TYPE_GUITARTABS       "GLYR_TYPE_GUITARTABS"
        TYPE_BACKDROPS        "GLYR_TYPE_BACKDROPS"

    ctypedef enum GLYR_ERROR:
        E_UNKNOWN       "GLYRE_UNKNOWN"
        E_OK            "GLYRE_OK"
        E_BAD_OPTION    "GLYRE_BAD_OPTION"
        E_BAD_VALUE     "GLYRE_BAD_VALUE"
        E_EMPTY_STRUCT  "GLYRE_EMPTY_STRUCT"
        E_NO_PROVIDER   "GLYRE_NO_PROVIDER"
        E_UNKNOWN_GET   "GLYRE_UNKNOWN_GET"
        E_INSUFF_DATA   "GLYRE_INSUFF_DATA"
        E_SKIP          "GLYRE_SKIP"
        E_STOP_POST     "GLYRE_STOP_POST"
        E_STOP_PRE      "GLYRE_STOP_PRE"
        E_NO_INIT       "GLYRE_NO_INIT"
        E_WAS_STOPPED   "GLYRE_WAS_STOPPED"

    ctypedef enum GLYR_FIELD_REQUIREMENT:
        REQUIRES_ARTIST "GLYR_REQUIRES_ARTIST"
        REQUIRES_ALBUM  "GLYR_REQUIRES_ALBUM"
        REQUIRES_TITLE  "GLYR_REQUIRES_TITLE"
        OPTIONAL_ARTIST "GLYR_OPTIONAL_ARTIST"
        OPTIONAL_ALBUM  "GLYR_OPTIONAL_ALBUM"
        OPTIONAL_TITLE  "GLYR_OPTIONAL_TITLE"

    ctypedef enum GLYR_GET_TYPE:
        GET_UNSURE             "GET_UNSURE"
        GET_COVERART           "GET_COVERART"
        GET_LYRICS             "GET_LYRICS"
        GET_ARTIST_PHOTOS      "GET_ARTIST_PHOTOS"
        GET_ARTISTBIO          "GET_ARTISTBIO"
        GET_SIMILAR_ARTISTS    "GET_SIMILAR_ARTISTS"
        GET_SIMILAR_SONGS      "GET_SIMILAR_SONGS"
        GET_ALBUM_REVIEW       "GET_ALBUM_REVIEW"
        GET_TRACKLIST          "GET_TRACKLIST"
        GET_TAGS               "GET_TAGS"
        GET_RELATIONS          "GET_RELATIONS"
        GET_ALBUMLIST          "GET_ALBUMLIST"
        GET_GUITARTABS         "GET_GUITARTABS"
        GET_BACKDROPS          "GET_BACKDROPS"
        GET_ANY                "GET_ANY"

###########################################################################
#                                 Structs                                 #
###########################################################################

    ctypedef struct inner_callback:
        void * user_pointer
        DL_callback func "download"

    ctypedef struct GlyrQuery:
        GLYR_GET_TYPE type
        int number
        int plugmax
        int verbosity
        size_t fuzzyness
        int img_min_size
        int img_max_size
        int parallel
        int timeout
        int redirects
        bool force_utf8
        bool download
        float qsratio
        bool db_autoread
        bool db_autowrite
        GlyrDatabase * local_db
        bool lang_aware_only
        int signal_exit
        char * lang
        char * proxy
        char * artist
        char * album
        char * title
        char * providers "from"
        char * allowed_formats
        char * useragent
        char * musictree_path
        inner_callback callback
        GLYR_ERROR q_errno
        GLYR_NORMALIZATION normalization

    ctypedef struct GlyrMemCache:
        char  * data
        size_t size
        char  * dsrc
        char * prov
        GLYR_DATA_TYPE data_type "type"
        int  duration
        int  rating
        bool is_image
        char * img_format
        unsigned char md5sum[16]
        bool cached
        double timestamp
        GlyrMemCache * next
        GlyrMemCache * prev

    ctypedef struct GlyrDatabase:
        char * root_path

    ctypedef struct GlyrFetcherInfo:
        char * name
        GLYR_GET_TYPE type
        GLYR_FIELD_REQUIREMENT reqs
        GlyrSourceInfo * head
        GlyrFetcherInfo * next
        GlyrFetcherInfo * prev

    ctypedef struct GlyrSourceInfo:
        char * name
        char key
        GLYR_GET_TYPE type
        int quality
        int speed
        bool lang_aware
        GlyrSourceInfo * next
        GlyrSourceInfo * prev

###########################################################################
#                                Functions                                #
###########################################################################

    # Init
    void glyr_init() nogil
    void glyr_cleanup() nogil
    char * glyr_version()

    # Query
    void glyr_query_init(GlyrQuery * query)
    void glyr_query_destroy(GlyrQuery * query)
    void glyr_signal_exit(GlyrQuery * query) nogil
    GlyrMemCache * glyr_get(GlyrQuery * query, void * p1, void * p2) nogil

    # Caches
    void glyr_free_list(GlyrMemCache * head)
    GlyrMemCache * glyr_cache_new()
    GlyrMemCache * glyr_cache_copy(GlyrMemCache * cache)
    void glyr_cache_free(GlyrMemCache * cache)
    void glyr_cache_set_dsrc(GlyrMemCache * cache, char * download_source)
    void glyr_cache_set_prov(GlyrMemCache * cache, char * provider)
    void glyr_cache_set_img_format(GlyrMemCache * cache, char * img_format)
    void glyr_cache_set_type(GlyrMemCache * cache, GLYR_DATA_TYPE type)
    void glyr_cache_set_rating(GlyrMemCache * cache, int rating)
    void glyr_cache_set_data(GlyrMemCache * cache, char * data, int len)
    void glyr_cache_update_md5sum(GlyrMemCache * cache)
    void glyr_cache_print(GlyrMemCache * cache)
    int glyr_cache_write(GlyrMemCache * cache, char * path)

    # Options
    GLYR_ERROR glyr_opt_dlcallback(GlyrQuery * settings, DL_callback dl_cb, void * userptr)
    GLYR_ERROR glyr_opt_type(GlyrQuery * s, GLYR_GET_TYPE type)
    GLYR_ERROR glyr_opt_artist(GlyrQuery * s, char * artist)
    GLYR_ERROR glyr_opt_album(GlyrQuery * s,  char * album)
    GLYR_ERROR glyr_opt_title(GlyrQuery * s,  char * title)
    GLYR_ERROR glyr_opt_img_minsize(GlyrQuery * s, int size)
    GLYR_ERROR glyr_opt_img_maxsize(GlyrQuery * s, int size)
    GLYR_ERROR glyr_opt_parallel(GlyrQuery * s, unsigned long parallel_jobs)
    GLYR_ERROR glyr_opt_timeout(GlyrQuery * s, unsigned long timeout)
    GLYR_ERROR glyr_opt_redirects(GlyrQuery * s, unsigned long redirects)
    GLYR_ERROR glyr_opt_useragent(GlyrQuery * s, char * useragent)
    GLYR_ERROR glyr_opt_lang(GlyrQuery * s, char * langcode)
    GLYR_ERROR glyr_opt_lang_aware_only(GlyrQuery * s, bool lang_aware_only)
    GLYR_ERROR glyr_opt_number(GlyrQuery * s, unsigned int num)
    GLYR_ERROR glyr_opt_verbosity(GlyrQuery * s, unsigned int level)
    GLYR_ERROR glyr_opt_from(GlyrQuery * s, char * provider_list)
    GLYR_ERROR glyr_opt_plugmax(GlyrQuery * s, int plugmax)
    GLYR_ERROR glyr_opt_allowed_formats(GlyrQuery * s, char * formats)
    GLYR_ERROR glyr_opt_download(GlyrQuery * s, bool download)
    GLYR_ERROR glyr_opt_fuzzyness(GlyrQuery * s, int fuzz)
    GLYR_ERROR glyr_opt_qsratio(GlyrQuery * s, float ratio)
    GLYR_ERROR glyr_opt_proxy(GlyrQuery * s, char * proxystring)
    GLYR_ERROR glyr_opt_force_utf8(GlyrQuery * s, bool force_utf8)
    GLYR_ERROR glyr_opt_lookup_db(GlyrQuery * s, GlyrDatabase * db)
    GLYR_ERROR glyr_opt_db_autowrite(GlyrQuery * s, bool write_to_db)
    GLYR_ERROR glyr_opt_db_autoread(GlyrQuery * s, bool read_from_db)
    GLYR_ERROR glyr_opt_musictree_path(GlyrQuery * s, char * musictree_path)
    GLYR_ERROR glyr_opt_normalize(GlyrQuery * s, GLYR_NORMALIZATION norm)

    # Reflection
    GlyrFetcherInfo * glyr_info_get()
    void glyr_info_free(GlyrFetcherInfo * info)

    # Enum <-> String
    char * glyr_data_type_to_string(GLYR_DATA_TYPE type)
    char * glyr_get_type_to_string(GLYR_GET_TYPE type)
    GLYR_GET_TYPE glyr_string_to_get_type(char * string)
    GLYR_DATA_TYPE glyr_string_to_data_type(char * string)
    char * glyr_strerror(GLYR_ERROR ID)

    # Checksums
    char * glyr_md5sum_to_string(unsigned char * md5sum)
    void glyr_string_to_md5sum(char * string, unsigned char * md5sum)

    # Weird
    GLYR_FIELD_REQUIREMENT glyr_get_requirements(GLYR_GET_TYPE type)

    # Various
    bool glyr_type_is_image(GLYR_GET_TYPE type)
    GlyrMemCache * glyr_download(char * url, GlyrQuery * s) nogil


cdef extern from "glyr/cache.h":
    # Database

    GlyrDatabase * glyr_db_init(char * root_path)
    void glyr_db_destroy(GlyrDatabase * db_object)
    GlyrMemCache * glyr_db_lookup(GlyrDatabase * db, GlyrQuery * query) nogil
    void glyr_db_insert(GlyrDatabase * db, GlyrQuery * q, GlyrMemCache * cache) nogil
    int glyr_db_delete(GlyrDatabase * db, GlyrQuery * query) nogil
    int glyr_db_edit(GlyrDatabase * db, GlyrQuery * query, GlyrMemCache * edited) nogil
    void glyr_db_replace(GlyrDatabase * db, unsigned char * md5sum, GlyrQuery * query, GlyrMemCache * data) nogil
    void glyr_db_foreach(GlyrDatabase * db, glyr_foreach_callback cb, void * userptr) nogil
    GlyrMemCache * glyr_db_make_dummy()


cdef extern from "glyr/misc.h":
    size_t glyr_levenshtein_strcmp(char * string, char * other) nogil
    size_t glyr_levenshtein_strnormcmp(char * string, char * other) nogil

cdef extern from "glyr/testing.h":
    char * glyr_testing_call_url(char * provider_name, GLYR_GET_TYPE type, GlyrQuery * query) nogil
    GlyrMemCache * glyr_testing_call_parser(char * provider_name, GLYR_GET_TYPE type, GlyrQuery * query, GlyrMemCache * cache) nogil

cdef extern from "glyr/config.h":
    enum:
        VERSION_MAJOR "GLYR_VERSION_MAJOR_INT"
        VERSION_MINOR "GLYR_VERSION_MINOR_INT"
        VERSION_MIRCO "GLYR_VERSION_MICRO_INT"
